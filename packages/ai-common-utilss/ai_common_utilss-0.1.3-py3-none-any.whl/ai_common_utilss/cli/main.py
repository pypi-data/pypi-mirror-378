import ai_text_utils
import ai_common_utilss
from ai_text_utils.text import GutenbergBooks, Tokenizer, create_dataloader, train_val_split,LSTMModel,gen_txt
from ai_common_utilss.trainer import Trainer
import torch
import torch.nn as nn
import torch.optim as optim
from functools import partial

def main():
    print({ai_text_utils.__version__})
    print({ai_common_utilss.__version__})

    book_ids = [
         {'start_id': 84, 'num_books': 1},
         #{'start_id': 2900, 'num_books': 4}
    ]
    books = GutenbergBooks("gutenberg_books")
    txt = books.get_books(book_ids)
    
    txt_arr = txt.split("<end_of_text>")

    #train_txt = "".join(txt_arr[:1])
    #val_txt = "".join(txt_arr[1:])
    train_txt, val_txt = train_val_split(txt, train_ratio=0.9)

    tokenizer = Tokenizer()
    seq_len=20
    batch_size=20
    vocab_size= tokenizer.vocab_size()
    emb_size=20
    hidden_size=30
    status_freq=1
    check_pt_freq=3
    epochs=10
    train_dl = create_dataloader(train_txt, 
                                 seq_len=seq_len, 
                                 batch_size=batch_size,
                                 shuffle=True,
                                 last_token_only=True)

    
    val_dl = create_dataloader(val_txt, 
                               seq_len=seq_len, 
                               batch_size=batch_size,
                               shuffle=True,
                               last_token_only=True)
    
    
    vocab_size
    criterion = nn.CrossEntropyLoss()
    model = LSTMModel(vocab_size=vocab_size, emb_size=emb_size, hidden_size=hidden_size)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    device= torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    trainer =Trainer()
    initial_txt= "These are my observations which "
    max_tokens=100
    gen_txt_callback = partial(gen_txt, model, initial_txt, device, tokenizer, seq_len,max_tokens)

    trainer.train(train_dl=train_dl,
                 val_dl=val_dl,
                 epochs=epochs,
                 model=model,
                 loss_fn=criterion,
                 optimizer=optimizer,
                 device=device,
                 status_freq=status_freq,
                 checkpoint_freq=check_pt_freq,
                 callback_freq=check_pt_freq,
                 callback=gen_txt_callback)
    
    
    
    