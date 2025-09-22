# AI Common Utils - Trainer Module

This repository contains a reusable trainer class for PyTorch model training.

## Installation

```bash
pip install ai-common-utils
```

## Usage:

```python

from ai_common_utils.trainer import Trainer

trainer = Trainer()
train_losses, train_accuracies, val_losses, val_accuracies= trainer.train(model=model,
                                                                        train_dl=train_dl,
                                                                        val_dl=val_dl,
                                                                        epochs=epochs,
                                                                        loss_fn=loss_fn,
                                                                        optimizer=optimizer,
                                                                        status_freq=20,
                                                                        checkpoint_freq=40,
                                                                        chk_point_file='model_weights.pth',
                                                                        device=device
                                                                        )
```

## Details
- **Returns**: Lists of (train_losses, train_accuracies, val_losses, val_accuracies) per epoch  
- **Progress**: Prints train/val metrics every `status_freq` batches  
- **Checkpoints**: Saves model weights to `chk_point_file` every `checkpoint_freq` batches
