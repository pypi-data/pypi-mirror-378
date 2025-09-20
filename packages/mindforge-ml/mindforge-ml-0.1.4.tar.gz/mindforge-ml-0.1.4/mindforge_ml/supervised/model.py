from mindforge_ml.datasets.loader import seq2seqdataset
from mindforge_ml.utils import tokenize, smart_tokenizer, ml_vocab_size, pad_token_id
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained("t5-base") #t5-base

# CUSTOM TRANSFORMER MODEL 


# -----------------------------
# Encoder-Decoder Transformer
# -----------------------------
class EncoderDecoderML(nn.Module):
    def __init__(self, vocab_size, d_model=256, nhead=8, num_encoder_layers=4, num_decoder_layers=4):
        super(EncoderDecoderML, self).__init__()

         # Shared embedding for encoder + decoder
        self.embedding = nn.Embedding(vocab_size, d_model)

        # Encoder
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_encoder_layers)

        #Decoder
        decoder_layer = nn.TransformerDecoderLayer(d_model, nhead)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_decoder_layers)

        # Output projection (to vocab logits)
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, query, target):
        """
        src: (batch, src_len)
        tgt: (batch, tgt_len) -> usually shifted right
        """

        # Embeddings
        src_emb = self.embedding(query).permute(1,0,2) # (src_len, batch, d_model)
        tgt_emb = self.embedding(target).permute(1, 0, 2)  # (tgt_len, batch, d_model)

        # memory
        memory = self.encoder(src_emb, src_key_padding_mask=(query == pad_token))
        
         # Decode (attends to encoder memory)
        out = self.decoder(
            tgt_emb,
            memory,
            tgt_key_padding_mask=(target == pad_token),
            memory_key_padding_mask=(query == pad_token)
        )

        # Project back to vocab
        logits = self.fc_out(out)  # (tgt_len, batch, vocab_size)

        return logits.permute(1, 0, 2)  # back to (batch, tgt_len, vocab_size)
    


pad_token = pad_token_id()
# -----------------------------
# Training + Prediction Wrapper
# -----------------------------
class MFTransformerSeq2Seq:
    def __init__(self, vocab_size, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        vocab_size = ml_vocab_size()
        self.model = EncoderDecoderML(vocab_size).to(self.device)
        self.criterion = nn.CrossEntropyLoss(ignore_index=pad_token)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=5e-5, betas=(0.9, 0.98), eps=1e-9, weight_decay=0.01)

    def fit(self, input_ids, attention_mask, labels, epochs=50, batch_size=32, verbose=True):


        train_dataset = TensorDataset(input_ids, attention_mask, labels)
        train_loader = DataLoader(train_dataset, batch_size, shuffle=True)

        self.train_loss = []
        self.train_acc = []

        for epoch in range(epochs):
            self.model.train()
            total_loss, total_correct, total_tokens = 0, 0, 0

            for query, atten_mask, target in train_loader:
                query, atten_mask, target = query.to(self.device), atten_mask.to(self.device), target.to(self.device)

                logits = self.model(query, target[:, :-1])  # (batch, tgt_len-1, vocab_size)
                loss = self.criterion(
                    logits.reshape(-1, logits.size(-1)),
                    target[:, 1:].reshape(-1)   # shift right
                )

                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)  # gradient clipping (helps stability)
                self.optimizer.step()

                total_loss += loss.item()

                 # Accuracy: compare predictions vs labels (ignoring pad)
                preds = torch.argmax(logits, dim=-1)  # (batch, tgt_len-1)
                correct = (preds == target[:, 1:]) & (target[:, 1:] != pad_token)
                total_correct += correct.sum().item()
                total_tokens += (target[:, 1:] != pad_token).sum().item()

            avg_loss = total_loss / len(train_loader)
            avg_acc = total_correct / total_tokens if total_tokens > 0 else 0

            self.train_loss.append(avg_loss)
            self.train_acc.append(avg_acc)

            if verbose:
                print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f} - Acc: {avg_acc:.4f}")

        return self.train_loss, self.train_acc
    
    
    def predict(self, query, max_len=50):
        self.model.eval()

        # 1. Tokenize user query
        inputs = tokenizer(
            query,
            max_length=512,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        ).to(self.device)

        query_ids = inputs["input_ids"]

        # 2. Start with <bos> (or pad_token if bos_token_id is missing)
        bos_token_id = tokenizer.bos_token_id or tokenizer.pad_token_id
        generated = torch.tensor([[bos_token_id]], device=self.device)

        # 3. Iterative decoding
        for _ in range(max_len):
            logits = self.model(query_ids, generated)
            next_token_logits = logits[:, -1, :]  # last predicted step

            # Greedy decoding (argmax)
            next_token_id = torch.argmax(next_token_logits, dim=-1).unsqueeze(0)
            generated = torch.cat([generated, next_token_id], dim=1)

            if next_token_id.item() == tokenizer.eos_token_id:
                break

        # 4. Decode prediction into text
        return tokenizer.decode(generated.squeeze().tolist(), skip_special_tokens=True)
