"""
CPU-GPU Double-Buffered Linear Module

This module implements a memory-efficient linear layer that keeps parameters on the CPU
and transfers them to the GPU on-demand for computation. It uses a double-buffering
strategy with asynchronous CUDA streams to overlap data transfers with computation,
effectively hiding the data transfer latency.

This approach is particularly useful for:
- Training very large models that do not fit entirely in GPU memory.
- Scenarios where GPU memory is a bottleneck, but high-throughput is still required.

The core idea is to use two sets of buffers for weights. While the GPU computes
the forward pass using one buffer, the data for the *next* layer's weights
is transferred from CPU to the other buffer in the background.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# dedicated stream for non-blocking data transfers
TRANSFER_STREAM = torch.cuda.Stream()

# --- Forward Pass Synchronization Primitives ---
# Event to signal that a forward pass data transfer has finished
TRANSFER_FORWARD_FINISHED_EVENT = torch.cuda.Event()
# Event to signal that the main compute stream is about to use the weights
COMPUTE_FORWARD_START_EVENT = torch.cuda.Event()
# Global double buffers for forward pass (weights and bias)
W_BUFFERS = [None, None]
B_BUFFERS = [None, None]

# --- Backward Pass Synchronization Primitives ---
# Event to signal that a backward pass data transfer has finished
TRANSFER_BACKWARD_FINISHED_EVENT = torch.cuda.Event()
# Event to signal that the main compute stream is about to use the weights for grad_input
COMPUTE_BACKWARD_START_EVENT = torch.cuda.Event()
# Separate double buffers for weight gradients in the backward pass
W_GRAD_BUFFERS = [None, None]

# Clock to alternate between the two buffers for forward and backward passes
FORWARD_BUFFER_CLK = 0
BACKWARD_BUFFER_CLK = 0


class BouncingLinearFn(torch.autograd.Function):
    """
    Custom autograd function for the double-buffered linear operation.

    This function orchestrates the asynchronous transfer of weights from CPU to GPU
    and synchronizes the compute stream to use the correct buffer, ensuring that
    data transfer and computation are overlapped.
    """

    @staticmethod
    def forward(ctx, x, weight_cpu, bias_cpu, device="cuda"):
        """
        Forward pass of the double-buffered linear layer.

        Args:
            ctx: PyTorch autograd context for saving backward pass information.
            x (torch.Tensor): Input tensor residing on the target GPU.
            weight_cpu (torch.Tensor): Weight matrix stored on the CPU.
            bias_cpu (torch.Tensor, optional): Bias vector stored on the CPU.
            device (str): The target GPU device for computation.

        Returns:
            torch.Tensor: The result of the linear transformation (x @ weight.T + bias).

        Flow:
            1. Select the current buffer based on the forward clock.
            2. On a dedicated transfer stream, wait for the previous compute operation to start.
            3. Initiate the asynchronous transfer of weights and bias to the selected GPU buffer.
            4. Record an event on the transfer stream to mark when the transfer is complete.
            5. Flip the clock to prepare for the next operation.
            6. On the main compute stream, wait for the data transfer to complete.
            7. Record an event to signal the start of the computation.
            8. Perform the linear operation using the now-ready GPU buffers.
        """
        global TRANSFER_STREAM, TRANSFER_FORWARD_FINISHED_EVENT, COMPUTE_FORWARD_START_EVENT, FORWARD_BUFFER_CLK, W_BUFFERS, B_BUFFERS

        # Select the buffer index using the clock
        selected_buffer = FORWARD_BUFFER_CLK

        # Enqueue the transfer on the dedicated transfer stream
        with torch.cuda.stream(TRANSFER_STREAM):
            # Wait for the main stream to signal it's starting its compute,
            # ensuring we don't overwrite a buffer that's still in use.
            TRANSFER_STREAM.wait_event(COMPUTE_FORWARD_START_EVENT)

            # Transfer weights and bias to the selected buffer. This is non-blocking.
            W_BUFFERS[selected_buffer] = weight_cpu.to(device, non_blocking=True)
            B_BUFFERS[selected_buffer] = (
                bias_cpu.to(device, non_blocking=True) if bias_cpu is not None else None
            )

            # Flip the clock for the next forward pass to use the other buffer
            FORWARD_BUFFER_CLK ^= 1
            # Record an event to mark the completion of this transfer
            TRANSFER_FORWARD_FINISHED_EVENT.record()

        # Make the main compute stream wait until the transfer is finished
        torch.cuda.current_stream().wait_event(TRANSFER_FORWARD_FINISHED_EVENT)

        # Signal that the compute operation is about to start
        COMPUTE_FORWARD_START_EVENT.record()
        # Perform the actual computation
        out = F.linear(x, W_BUFFERS[selected_buffer], B_BUFFERS[selected_buffer])

        # Save necessary tensors for the backward pass
        ctx.save_for_backward(x, weight_cpu, bias_cpu)
        ctx.device = device
        return out

    @staticmethod
    def backward(ctx, grad_out):
        """
        Backward pass for gradient computation.

        Args:
            ctx: Autograd context with saved tensors from the forward pass.
            grad_out (torch.Tensor): Gradient with respect to the layer's output.

        Returns:
            tuple: Gradients w.r.t. (input, weight, bias, device).
                   The gradient for the device argument is None.

        Note:
            Weights are transferred again for the `grad_input` calculation,
            following the same double-buffering pattern as the forward pass.
        """
        global TRANSFER_STREAM, TRANSFER_BACKWARD_FINISHED_EVENT, COMPUTE_BACKWARD_START_EVENT, BACKWARD_BUFFER_CLK, W_GRAD_BUFFERS

        # Select the buffer index using the backward clock
        selected_buffer = BACKWARD_BUFFER_CLK

        x, weight_cpu, bias_cpu = ctx.saved_tensors
        device = ctx.device

        # Enqueue weight transfer on the dedicated stream for grad_input calculation
        with torch.cuda.stream(TRANSFER_STREAM):
            # Wait for the previous backward compute to start before overwriting the buffer
            TRANSFER_STREAM.wait_event(COMPUTE_BACKWARD_START_EVENT)

            # Transfer weights needed for grad_input = grad_out @ w
            W_GRAD_BUFFERS[selected_buffer] = weight_cpu.to(device, non_blocking=True)

            # Flip the clock for the next backward pass
            BACKWARD_BUFFER_CLK ^= 1
            # Record an event to mark the completion of this transfer
            TRANSFER_BACKWARD_FINISHED_EVENT.record()

        # Make the compute stream wait for the weight transfer to complete
        torch.cuda.current_stream().wait_event(TRANSFER_BACKWARD_FINISHED_EVENT)

        # Signal that the backward compute is about to start
        COMPUTE_BACKWARD_START_EVENT.record()

        # Compute gradients
        grad_input = grad_out @ W_GRAD_BUFFERS[selected_buffer]
        grad_weight = grad_out.t() @ x
        grad_bias = grad_out.sum(dim=0) if bias_cpu is not None else None

        return grad_input, grad_weight, grad_bias, None


class CPUBouncingLinear(nn.Module):
    """
    A linear layer with CPU-resident parameters that are "bounced" to the GPU
    on demand using a double-buffering strategy to hide transfer latency.

    This module acts as a drop-in replacement for `nn.Linear` but is designed
    for memory-constrained environments.

    Trade-offs:
    + Greatly reduces GPU memory footprint, enabling larger models.
    - Introduces latency that must be hidden by sufficient computation or batch size.
    - Assumes forward and backward passes on layers are sequential.
    """

    def __init__(self, in_features, out_features, bias=True, device="cuda"):
        """
        Initializes the CPUBouncingLinear layer.

        Args:
            in_features (int): The number of input features.
            out_features (int): The number of output features.
            bias (bool): If True, adds a learnable bias to the output.
            device (str): The target GPU device for computation.
        """
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.device = device

        # Parameters are created and live on the CPU
        self.weight = nn.Parameter(torch.empty(out_features, in_features, device="cpu"))
        self.bias = (
            nn.Parameter(torch.empty(out_features, device="cpu")) if bias else None
        )

        # Note: Parameter initialization is expected to be done externally
        # to ensure consistency with corresponding GPU versions in a model.

    def init_from_tensor(self, weight_tensor, bias_tensor=None):
        """
        Initializes the layer's parameters from existing tensors.

        This method is useful for loading pretrained weights or ensuring consistent
        initialization across different model configurations.

        Args:
            weight_tensor (torch.Tensor): The tensor to use for the weights.
            bias_tensor (torch.Tensor, optional): The tensor to use for the bias.
        """
        self.weight.data.copy_(weight_tensor.cpu())
        if self.bias is not None and bias_tensor is not None:
            self.bias.data.copy_(bias_tensor.cpu())

    def forward(self, x):
        """
        Performs the forward pass of the linear layer.

        Args:
            x (torch.Tensor): The input tensor, which should reside on the target GPU.

        Returns:
            torch.Tensor: The output tensor after the linear transformation.
        """
        return BouncingLinearFn.apply(x, self.weight, self.bias, self.device)
