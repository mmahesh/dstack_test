
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from torchvision.datasets import MNIST
from torchvision import transforms
import pytorch_lightning as pl
import argparse

class LitAutoEncoder(pl.LightningModule):
	def __init__(self):
		super().__init__()
		self.encoder = nn.Sequential(
                    nn.Linear(28 * 28, 64),
                    nn.ReLU(),
                    nn.Linear(64, 3))
		self.decoder = nn.Sequential(
                    nn.Linear(3, 64),
                    nn.ReLU(),
                    nn.Linear(64, 28 * 28))

	def forward(self, x):
		embedding = self.encoder(x)
		return embedding

	def configure_optimizers(self):
		optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
		return optimizer

	def training_step(self, train_batch, batch_idx):
		x, y = train_batch
		x = x.view(x.size(0), -1)
		z = self.encoder(x)
		x_hat = self.decoder(z)
		loss = F.mse_loss(x_hat, x)
		self.log('train_loss', loss)
		return loss

	def validation_step(self, val_batch, batch_idx):
		x, y = val_batch
		x = x.view(x.size(0), -1)
		z = self.encoder(x)
		x_hat = self.decoder(z)
		loss = F.mse_loss(x_hat, x)
		self.log('val_loss', loss)


# data
dataset = MNIST('data', train=True, download=True,
                transform=transforms.ToTensor())
mnist_train, mnist_val = random_split(dataset, [55000, 5000])

train_loader = DataLoader(mnist_train, batch_size=32)
val_loader = DataLoader(mnist_val, batch_size=32)

# model
model = LitAutoEncoder()

parser = argparse.ArgumentParser(description='PyTorch Lightning MNIST Example')
parser.add_argument('--gpus', type=int, default=1)
parser.add_argument('--precision', type=int, default=16)
parser.add_argument('--limit_train_batches', type=float, default=0.5)

args = parser.parse_args()



# # training
trainer = pl.Trainer(accelerator='gpu', gpus=args.gpus, precision=args.precision,
                     limit_train_batches=args.limit_train_batches)
trainer.fit(model, train_loader, val_loader)


