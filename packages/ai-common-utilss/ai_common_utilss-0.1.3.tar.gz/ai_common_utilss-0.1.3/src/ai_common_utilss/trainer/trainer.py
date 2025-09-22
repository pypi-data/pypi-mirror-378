from contextlib import contextmanager, nullcontext
import torch
from datetime import datetime

class Trainer():
    def __init__(self):
        pass
    
    def train(self, train_dl, 
                    val_dl, 
                    epochs, 
                    model, 
                    optimizer, 
                    loss_fn, 
                    device, 
                    chk_point_file=None, 
                    status_freq=20, 
                    checkpoint_freq=50,
                    callback_freq=20,
                    callback=None
                    ):
        if (chk_point_file is None):
            chk_point_file = 'model_weights.pth'
        
        model.to(device)
        
        # Get dataset sizes
        n_train_batches = len(train_dl)
        n_val_batches = len(val_dl)
        train_size = n_train_batches * train_dl.batch_size
        val_size = n_val_batches * val_dl.batch_size
        print(f'Training set size: {train_size} samples ({n_train_batches} batches)')
        print(f'Validation set size: {val_size} samples ({n_val_batches} batches)')
        
        train_accuracies = []
        val_accuracies = []
        train_losses =[]
        val_losses = []
        
        for epoch in range(epochs):
            total_loss , total_correct = 0.0, 0.0
            train_loss, train_acc = forward_pass(model,device, train_dl, loss_fn, optimizer, True)
            val_loss, val_acc = forward_pass(model,device, val_dl, loss_fn, None, False)
            train_accuracies.append(train_acc)
            train_losses.append(train_loss)
            val_accuracies.append(val_acc)
            val_losses.append(val_loss)
            if (epoch % status_freq == 0 ) :
                print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Epoch {epoch:05d} : train_loss={train_loss}, train_acc={train_acc} | Val_loss={val_loss}, val_acc={val_acc}')
            if (epoch % checkpoint_freq == 0 ) :
                print(f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Epoch {epoch:05d} : saving model weights in {chk_point_file}')
                torch.save(model.state_dict(), chk_point_file)
            if (epoch % checkpoint_freq == 0 ) :
                if (callback):
                    callback()
        return train_losses, train_accuracies, val_losses, val_accuracies
        
def forward_pass(model,device, dl, loss_fn, optimizer, is_training):
    total_count = 0
    total_loss , total_correct = 0.0, 0.0
    
    with set_mode(model, is_training):
        for i, (X, y) in enumerate(dl):
            X, y = X.to(device), y.to(device)
            y_pred = model(X)
            loss = loss_fn(y_pred, y)
            if (is_training):
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item()
            # Get predicted class indices by taking argmax along last dimension
            predictions = torch.argmax(y_pred, dim=-1)
            correct = (predictions == y).sum().item()
            total_correct += correct
            total_count +=X.shape[0]
    acc = 100 * total_correct / total_count
    avg_loss = total_loss / total_count
    return avg_loss, acc

@contextmanager
def set_mode(model, is_training):
    if (is_training):
        model.train()
        ctx = nullcontext()
    else: 
        model.eval()
        ctx = torch.no_grad()
    with ctx:
        yield
    


    


    