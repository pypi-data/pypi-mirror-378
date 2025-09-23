# Changelog

All notable changes to forgeNN will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [Unreleased]

## [2.0.0] - 2025-09-17

### Highlights
- V2 architecture: internal re-organization, device/runtime/backends scaffolding, and ONNX stubs. Public training API remains familiar (`Sequential`, `compile/fit/evaluate/predict`).
- Transformer groundwork lands: Multi-Head Attention with causal masking and a pre-LN Transformer block for upcoming GPT-style models.

### Added
- New `forgeNN/nn/` package consolidating `activations`, `losses`, `metrics` and `random` with simple registries.
- Runtime device API in `forgeNN/runtime/device.py`:
  - `get_default_device`, `set_default_device`, `is_cuda_available`, and `use_device(...)` context manager.
- Backends scaffold in `forgeNN/backends/`:
  - `cpu.py` NumPy backend and `cuda.py` placeholder (optional CuPy-based; raises if CuPy missing).
- ONNX Export – Stage 1 (MVP) complete in `forgeNN/onnx/io.py`:
  - Export supported for Sequential MLPs with: `Input`, `Dense`→`Gemm` (auto `transB`), `Flatten`, and activations (`Relu`, `Sigmoid`, `Tanh`; optional `Softmax`).
  - `Dropout` is folded away in eval mode (skipped during export).
  - Default opset 13; forces IR v10 for compatibility with older onnxruntime builds.
  - Parity verified with onnxruntime (max diff ~1e-6). TensorFlow via onnx-tf is optional and may require tensorflow-addons (Windows caveat).
  - Import implemented (see ONNX Import – Stage 1 below).
- ONNX Import – Stage 1 in `forgeNN/onnx/io.py`:
  - `load_onnx(path, strict=True)` imports linear MLP graphs with `Gemm` (honors `alpha`, `beta`, `transB`), `Flatten(axis=1)`, and activations (`Relu`, `Sigmoid`, `Tanh`, `Softmax`).
  - Skips benign `Identity`/`Dropout`. Builds a `Sequential` (adds `Input` if known), assigns `Dense` weights/biases.
  - Strict mode raises on unsupported ops; designed for simple feed‑forward graphs.
- Optional extras in packaging: `[onnx]`, `[cuda]`, and `[all]` in `pyproject.toml`.
- New docs: `ARCHITECTURE.md` plus short READMEs under `runtime/`, `backends/`, and `onnx/` describing intent.
- Examples:
  - `examples/device_api_demo.py` showing device API usage and a quick 1-epoch run.
  - `examples/onnx_example.py` training a small MLP, exporting to ONNX, and running it via onnxruntime (fallback) or TensorFlow (onnx-tf) with parity checks.
  - `examples/onnx_roundtrip.py` training → export → import → parity assert and accuracy check.
  - `examples/adam_quickstart.py` now supports live accuracy plotting during training if `matplotlib` is available (falls back to single fit otherwise).
 - Module-level convenience API:
   - `forgeNN.randint(low, high, size)` returns a NumPy `ndarray` of dtype `int64` for fast dataset indexing (not a `Tensor`).
   - `forgeNN.stack(list, axis=0)` stacks Tensors or array-like values into a new `Tensor`; gradients propagate only into Tensor inputs.
 - Tensor ergonomics:
   - NumPy-style indexing and slicing via `Tensor.__getitem__` with correct gradient scatter-back into the sliced region.
   - `Tensor.tolist()` helper for readable printing (returns a Python scalar for 0-D tensors).
 - Public API ergonomics:
   - Exposed the `nn` subpackage at top-level (`import forgeNN as fnn; fnn.nn.set_seed(...)`).
   - RNG utilities (`forgeNN.nn.random`) simplified to manage NumPy and Python `random` states only; re-exported at `fnn.nn`.
 - New Layers - foundational building blocks for upcoming Transformer support:
   - `Embedding(vocab_size, embedding_dim, padding_idx=None)`: vector lookup with correct gradient accumulation via `np.add.at`; supports optional frozen padding row.
   - `LayerNorm(normalized_shape=None, eps=1e-5)`: last-dim normalization with learnable affine parameters (gamma/beta) and lazy init.
   - `GlobalAvgPool1D(keepdims=False)` and `GlobalAvgPool2D(keepdims=False)`: reduction over temporal/spatial dims using Tensor.mean; integrates with `Sequential.summary()`.
   - Conv1D and MaxPool1D implementations (stride support; valid padding only). Autograd-safe via Tensor slicing/stack/matmul. Exported at top level.
   - Conv2D and MaxPool2D implementations (NCHW; rectangular kernels/strides; valid padding only). Autograd-safe sliding-window implementation. Exported at top level.
 - Model serialization utilities in `forgeNN/model/io.py`:
   - `state_dict(model)`, `load_state_dict(model, state)`
   - `save_npz(path, model)`, `load_npz(path)`
 - Transformer components (initial):
   - `MHA` / `MultiHeadAttention`: scaled dot-product self-attention with cached causal mask, attention dropout, and output projection dropout.
   - `TransformerBlock`: pre-LN block composed of `LayerNorm` → `MHA` → residual, then `LayerNorm` → `Dense` → GELU → `Dense` → dropout → residual.
   - Exported at top-level API for convenience: `from forgeNN import MHA, MultiHeadAttention, TransformerBlock`.
 - Examples:
   - `examples/embedding_layernorm_text_classification.py`: fastText-style classifier showing Embedding → GlobalAvgPool1D → LayerNorm → Dropout → Dense on a synthetic dataset.
   - `examples/embedding_layernorm_text_classification.md`: step-by-step README explaining data generation, model, training, troubleshooting, and extensions.

### Changed
- Core Tensor moved to `forgeNN/core/tensor.py`. The original `forgeNN/tensor.py` now re-exports as a temporary compatibility shim.
- All internal modules and examples updated to import `Tensor` from `forgeNN.core.tensor` (please migrate your imports accordingly).
- `Dropout` fully rewritten with inverted scaling and clear train/eval behavior; lower overhead.
- `ActivationWrapper` now caches/uses pre-resolved activation callables to avoid per-forward overhead.
- Defaults aligned for smoother training parity with Keras/TensorFlow:
  - Adam `eps=1e-7` and float32 parameter/math defaults.
- Initialization and shapes:
  - `Dense` uses Xavier/Glorot init; `Flatten` simplified; `Input` clarified for summary/shape seeding.
 - Public API ergonomics (cont.):
   - `randint`/`stack` are now available at the top level (`import forgeNN as fnn; fnn.randint(...), fnn.stack(...)`).
   - `forgeNN.randint` intentionally returns a NumPy array (indices), while `forgeNN.stack` accepts both Tensors and array-likes and returns a `Tensor`.
 - Layer naming consistency: renamed placeholders `Convo1D/Convo2D` to `Conv1D/Conv2D`.
 - Top-level exports: added `Embedding`, `LayerNorm`, `GlobalAvgPool1D`, and `GlobalAvgPool2D` to `forgeNN.__init__` for direct import.
 - Top-level exports (cont.): added `MHA`, `MultiHeadAttention`, and `TransformerBlock` under `forgeNN.__init__`.
 - `Sequential.summary()` shape inference enhanced to recognize GlobalAvgPool layers (handles keepdims output forms) and Embedding (appends `embedding_dim`).
 - Activation registry: added `'softmax'` (and `'gelu'`) to `forgeNN/nn/activations.py`.
 - Public API: exported `Conv1D`, `MaxPool1D`, `Conv2D`, `MaxPool2D`, and model IO helpers from `forgeNN.__init__`. 

### Fixed
- Broadcasting-aware gradient reductions centralized (`_sum_to_shape`) for add/mul and friends.
- Proper gradients for division, including right-division (`__rtruediv__`).
- `mean.backward` supports tuple axes with correct scaling; `max.backward` stabilized for ties with epsilon.
 - Example compatibility: `examples/transformer/gpt.py` now runs end-to-end. Resolved earlier errors by introducing `Tensor` slicing support and aligning `randint` (returns indices array) and `stack` semantics.
 - Prevented import-time crashes from unimplemented layer stubs (Conv/Pool/BatchNorm) by moving `NotImplementedError` to `__init__/forward` instead of class body scope.
 - Validation/evaluation now run with layers in eval mode (disables Dropout): training utilities toggle `train()/eval()` automatically during `evaluate()` and `predict()`, and keep training mode during minibatches in `fit`. This removes excessive validation jitter and matches Keras behavior.
 - ONNX export: Lazily initialize `Dense` parameters from inferred input features during export when uninitialized, fixing `AttributeError: 'NoneType' object has no attribute 'data'` for fresh models.

### Deprecated
- Top-level `forgeNN/tensor.py` is a compatibility shim. It will be removed in a future release—please update imports to `forgeNN.core.tensor`.
- `vectorized.py` kept only as a light shim; prefer `nn/` + `Sequential` path.
 - `Tensor.stack(...)` and `Tensor.randint(...)` are deprecated in favor of the module-level `forgeNN.stack` and `forgeNN.randint` (emit `DeprecationWarning`; shims forward to the new APIs).

### Removed
- Aggressive cleanup of unused/deprecated assets: old guides, legacy scripts, and test scaffolding.
 - Experimental Colab notebook and early transformer example scripts were removed to keep the repository lean; the `examples/transformer/` folder currently serves as a placeholder for future, smaller examples.

### Performance
- Small speedups from reduced activation wrapper overhead, simplified shape inference, and fused gradient reductions.

### Notes
- CUDA remains a scaffold at this time: backend is not wired to Tensor ops yet.
- ONNX export Stage 1 (subset) and import Stage 1 (linear MLP graphs) are implemented.
- Transformer notes: `PositionalEncoding` and `PositionalEmbedding` remain stubs raising `NotImplementedError` and are planned for a subsequent 2.x minor.
- Public API remains familiar; examples updated accordingly. A deprecation window exists for the `Tensor` import path via the shim.
- Conv/Pool currently support stride; padding/dilation are not yet implemented and will raise `NotImplementedError`.

#### ONNX Export (Stage 1) Details
- Scope: Sequential-only, feed-forward MLP graphs without branches.
- Ops: `Gemm` (Dense), `Relu`/`Sigmoid`/`Tanh` (activations), `Flatten`, optional `Softmax` at the end, `Input` placeholder. `Dropout` is folded in eval and skipped.
- Shapes: output `ValueInfo` carries symbolic batch ("N") and concrete feature dims; passes ONNX checker and shape inference.
- Tooling: exports with opset 13; sets IR to 10 for older onnxruntime (configurable). Parity tested on Windows via onnxruntime. onnx-tf works when TensorFlow + tensorflow-addons are properly installed (Linux easiest).

#### ONNX Import (Stage 1) Details
- Scope: Linear, feed‑forward MLP graphs without branches.
- Ops: `Gemm` with `alpha`/`beta`/`transB` handled, `Flatten(axis=1)`, activations (`Relu`, `Sigmoid`, `Tanh`, `Softmax`). `Identity` and `Dropout` are skipped.
- Behavior: Builds a `Sequential` model (adds `Input` if shape known from model I/O), attaches activations adjacent to `Gemm`, and assigns parameters to `Dense` layers in order.
- Example: See `examples/onnx_roundtrip.py` for export → import → parity assertion workflow.

## [1.3.1] - 2025-09-13

### Changed
- Corrected the README content to accurately reflect the training API and available features.

## [1.3.0] - 2025-09-10

### Last Major Release Before 2.x Update!

### Added
- Added `Dropout` layer with training/inference modes and integrated into `Sequential`.
- New example `examples/dropout_example.py` demonstrating dropout regularization on MNIST with accuracy plots.
- (Docs) Clarified improved `mse` behavior (auto one-hot + regression reshaping) and availability of `model.summary()` in README.
- Modular optimizer system with new classes: `SGD`, `Adam`, and `AdamW` (decoupled weight decay)
- Deferred optimizer parameter binding (`opt = Adam(lr=1e-3)` then pass instance directly to `compile`)
- Ability to pass optimizer instances OR dict configs (`{"type":"adam", "lr":1e-3}` still supported)
- Optimizer public base class `Optimizer` exported at top level
- New example `optimizer_convergence_demo.py` comparing SGD vs Adam convergence
- Unit tests planned for optimizer correctness (bias correction, decoupled decay) added in test suite

### Changed
- Optimized training loop: removed redundant full-dataset forward after each epoch; metrics now aggregated on-the-fly (no API change).
- Fused stable softmax + cross-entropy implementation reduces intermediate allocations and duplicate exponentials.
- Documentation and guides updated to reflect new optimizer API (Sequential & Training guides, Comparison guide)
- Adam optimizer default `eps` changed to `1e-7` for improved numerical stability (matches PyTorch/TensorFlow defaults)
- Vectorized class now uses dtype float32 consistently for weights and biases (was float64 in some cases)
### Fixed
- Ensured `mse` consistently handles (N,) integer class targets vs. (N,C) logits without user-side one-hot conversion.

### Deprecated
- Legacy `VectorizedOptimizer` name now an alias of `SGD` (will be removed in a future major release)

### Performance
- Minor speed improvement from fused cross-entropy and eliminated extra per-epoch evaluation pass.

### Notes
- No breaking changes; public APIs (`compile().fit`, losses, metrics) unchanged.
- Dropped experimental acceleration path (Numba) before release—kept code lean and dependency surface minimal.

## [1.2.1] - 2025-09-09

### Added
- Keras-like `Sequential.summary()` method with symbolic shape inference:
  - Displays layer type (including attached activation), inferred output shape, and parameter counts
  - Automatically initializes lazily defined `Dense` layers when input feature size can be inferred
  - Supports optional `Input` layer to seed shape propagation or an explicit `input_shape` argument
- New `Input` layer (shape placeholder) exported at top level; integrates with summary and symbolic inference
- Auto one-hot + regression reshaping logic in `mse` improved (classification targets converted when 1D indices and logits are 2D)

### Changed
- Restored lazy initialization semantics for `Dense` during forward, while allowing summary to perform safe symbolic initialization when shapes are fully known
- Summary now keeps unresolvable shapes as `?` instead of forcing initialization (safer for partially dynamic pipelines)
- Documentation (guides) updated to reflect `Input` layer usage and model introspection via `model.summary()`

### Fixed
- Resolved missing `Sequential.summary` attribute caused by earlier nested definition bug
- Ensured parameter counts include activation-wrapped layers consistently

### Notes
- No breaking API changes; existing models continue to work
- `Input` layer is optional—models without it still summarize if `input_shape` is passed or shapes become inferable after first forward

### Upcoming (Planned)
- Potential inclusion of concatenation (`cat`) and stacking utilities per TODO roadmap
- Extended summary statistics (dtype, trainable flags) in future minor release


## [1.2.0] - 2025-09-08

### Added
- High-level layering API:
  - `Layer` base class and `ActivationWrapper` using the `@` operator to attach activations
  - `Sequential` container for ordered composition of layers
  - `Dense` (lazy init) and `Flatten` layers
  - Placeholders for `Conv2D` and `MaxPool2D` (raise NotImplementedError for now)
- Keras-like trainer utilities:
  - `compile(model, optimizer, loss, metrics)` returning a `CompiledModel`
  - `fit`, `evaluate`, and `predict` helpers
  - Built-in loss registry (`cross_entropy`) and metric registry (`accuracy`)
  - Mean Squared Error loss (`mse`) implemented in `forgeNN.vectorized` and registered in the trainer loss registry (usable via `loss="mse"` in `compile`)
- Documentation & guides:
  - New `SEQUENTIAL_GUIDE.md` explaining the Sequential API with comparisons to PyTorch and Keras
  - New `TRAINING_GUIDE.md` mapping Keras/PyTorch training to `compile/fit`
  - Updated `README.md` with `compile/fit` examples and guide links
- Examples:
  - New `examples/sequential_mnist.py` using `Sequential` and `compile/fit`
  - Updated `examples/benchmark_mnist.py` to use `Sequential + compile/fit` while keeping PyTorch comparison and plots
- Testing:
  - Expanded unit tests for `Sequential`, `Dense` lazy init, activation handling (string/class/callable), `Flatten`, nested `Sequential.zero_grad`, and optimizer momentum buffers
  - Ensured optimizer works with lazy-initialized `Dense` by performing a dummy forward prior to optimizer construction
- Public API:
  - Exported `Sequential`, `Dense`, `Flatten`, `ActivationWrapper`, and `compile` from the top-level package

### Changed
- Trainer stability and metric aggregation:
  - `CompiledModel.fit`/`evaluate` now aggregate loss and metrics weighted by batch size
  - `evaluate` computes accuracy via total correct/total samples for exact dataset accuracy
- Benchmark updates:
  - `examples/benchmark_mnist.py` now seeds NumPy for reproducibility and uses batch size 64
  - Per-epoch metrics are collected via `evaluate` to reduce jitter in plots
- Documentation/docstrings:
  - Comprehensive docstrings across `tensor.py` and `vectorized.py` with cleaned examples
  - Fixed `cross_entropy_loss` docstring to show correct gradient shape `(2, 2)`
 - Demo notebook training settings tuned for small datasets (increased epochs, reduced batch size, slightly higher learning rate) and updated to use the current `evaluate(X, y)` signature

### Deprecated
- Direct use of `VectorizedMLP`+manual training loops in examples in favor of `Sequential + compile/fit`
  - These APIs remain available for 1.x but are slated for removal/refactor in a future 2.x release
- Legacy training snippets in guides superseded by `compile/fit` sections

### Fixed
- Accuracy wobble in benchmarks by switching to sample-weighted aggregation and exact accuracy counting
- Lazy-init + optimizer ordering issue in tests by adding a dummy forward before optimizer/trainer creation
 - Implemented `mse` using graph composition (`(pred - target)**2 .mean()`) to ensure correct gradient scaling across all elements and robust broadcasting
 - Prevented unintended broadcasting for single-logit outputs by reshaping 1D targets `(N,)` to `(N, 1, ...)` when logits have singleton non-batch dimensions

### Security
- No security-related changes in this release

## [1.1.1] - 2025-09-08
### Added
- Added comprehensive documentation for all of the methods. Now the API is fully documented. If you see any missing docstrings, please open an issue.
- Added `elu()` activation function with proper tensor integration
- Added unit tests for `elu()` function

### Fixed
- 

## [1.1.0.1] - 2025-09-08
### Added
- Added `dot()` method for 1D tensor dot product with autograd support
- Added `GELU` activation function with proper tensor integration
- Added unit tests for `dot()` and `GELU` functions

### Fixed
- Fixed minor bug in `VectorizedLayer` activation handling
- Improved error messages for tensor shape operations
- Enhanced documentation for new tensor methods

## [1.1.0] - 2025-09-07

### MAJOR CLEANUP - Legacy Removal
- **REMOVED**: Entire `forgeNN.legacy` module - no longer maintained
- **REMOVED**: Backward compatibility code and comments
- **CLEAN**: Simplified API focused on modern, high-performance components
- **FOCUS**: Pure vectorized operations for maximum speed

### Enhanced
- **Unified activation system**: String/class/callable activations fully integrated
- **Cleaner documentation**: Removed outdated legacy references
- **Modern API**: Streamlined imports and cleaner codebase

## [1.0.4a0] - 2025-09-07

### Added
- **Activation function integration**: Full tensor integration for all activation functions
- **New tensor methods**: `leaky_relu()` and `swish()` with proper gradients
- **Enhanced VectorizedLayer**: Supports string, class, and callable activations
- **Clean loss API**: Removed confusing `functions.loss` module

## [1.0.4] - 2025-09-07

### Added
- **Complete tensor shape operations suite**
  - `reshape()` - Change tensor dimensions with automatic size inference
  - `view()` - Memory-efficient reshape operation
  - `flatten()` - Convert multidimensional tensors to 1D
  - `contiguous()` - Ensure memory contiguity for operations
  - `transpose()` - Swap tensor dimensions with proper gradient flow
  - `squeeze()` - Remove dimensions of size 1
  - `unsqueeze()` - Add dimensions of size 1
- **Matrix multiplication operations**
  - Full `@` operator support with broadcasting
  - Proper gradient computation for backpropagation
  - Support for batch matrix operations
- **Comprehensive test suite**
  - 40 unit tests covering all tensor operations
  - Complete gradient flow validation
  - Edge case testing and error handling
  - 100% test pass rate
- **Performance benchmarks and documentation**
  - MNIST benchmark showing 2.10x speedup over PyTorch
  - Detailed PyTorch vs forgeNN comparison guide
  - Live demo script for framework comparison
  - Professional documentation and examples

### Enhanced
- **VectorizedMLP performance improvements**
  - Optimized for small models (3.52x faster than PyTorch on <109k parameters)
  - Better accuracy on MNIST (97.37% vs PyTorch's 97.30%)
  - Xavier weight initialization for improved training dynamics
- **Gradient computation reliability**
  - Fixed dimension tracking in squeeze operations
  - Improved numerical stability in loss functions
  - Enhanced autograd system for complex operation chains
- **Code quality and organization**
  - Clean repository structure with professional .gitignore
  - Comprehensive error handling and validation
  - Consistent API design across all operations

### Documentation
- **README.md** - Updated with performance highlights and quick start guide
- **COMPARISON_GUIDE.md** - Detailed framework comparison with benchmarks
- **Comprehensive examples** - Complete MNIST classification example
- **API documentation** - Clear docstrings for all public methods

### Technical Improvements
- All tensor operations now support proper autograd
- Memory-efficient implementations for large tensor operations
- Robust error handling for shape mismatches
- Professional logging and debugging support

### Performance
- 2.10x faster MNIST training compared to PyTorch
- 3.52x speedup on small models (<109k parameters)
- Efficient vectorized operations using NumPy backend
- Minimal memory overhead for gradient computation

### Breaking Changes
None - All changes are backward compatible

### Migration Guide
No migration required - existing code will continue to work unchanged.

## [1.0.0] - 2025-09-06

### Added
- Initial release of forgeNN framework
- Vectorized automatic differentiation with `Tensor` class
- High-performance `VectorizedMLP` implementation
- Legacy educational implementations in `forgeNN.legacy`
- Complete activation function library
- Professional loss functions (cross-entropy, MSE)
- Vectorized optimizer with momentum support
- Comprehensive MNIST example achieving 93%+ accuracy
- Full documentation and performance guides
- PyPI-ready packaging configuration

### Features
- **Vectorized Operations**: NumPy-powered batch processing (100x+ speedup)
- **Dynamic Computation Graphs**: Automatic differentiation with gradient tracking
- **Complete Neural Networks**: From simple neurons to complex architectures
- **Production Loss Functions**: Cross-entropy, MSE with numerical stability
- **Educational Components**: Legacy implementations for learning purposes
- **High Performance**: 38,000+ samples/sec training speed

### Performance
- MNIST classification: 93%+ accuracy in under 2 seconds
- Training speed: 38,000+ samples per second
- Memory efficient vectorized operations
- Optimized backward pass implementations

### Documentation
- Comprehensive README with examples
- Performance optimization guide
- Activation function reference guide
- Complete installation instructions
- Full API documentation in docstrings

### Examples
- Complete MNIST classification demo
- Performance benchmarking examples
- Educational automatic differentiation examples
- Production-ready training loops

## [0.1.0] - 2025-09-01

### Added
- Initial development version
- Basic automatic differentiation engine
- Simple neural network implementations
- Educational examples and tutorials
