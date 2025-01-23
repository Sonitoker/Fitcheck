import torch.nn as nn
from src.config import config as cfg
from torchvision import models


class CompatibilityModel(nn.Module):
    """Custom model to measure compatibility between fashion products"""

    """
        Initializes the compatibility model with a ResNet-18 base model and embedding layers.
        
        Args:
            hidden_dim (int): Dimension of the hidden layer in the embedding layers.
            emb_dim (int): Dimension of the final embedding output.
            dropout (float): Dropout rate for regularization.
        """
    def __init__(self, hidden_dim=cfg.HIDDEN_DIM, emb_dim=cfg.EMBEDDING_DIM, dropout=cfg.DROPOUT):
        super(CompatibilityModel, self).__init__()
        # use resnet34 as base model
        self.create_base_model()
        # add 2 layers on top of base model
        self.embedding_layers = nn.Sequential(
            nn.Linear(512, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, emb_dim),
        )

    """
        Sets up the base model by loading a pre-trained ResNet-18 and replacing the final 
        fully connected layer with an identity layer.
        """
    def create_base_model(self):
        self.base_model = models.resnet18(pretrained=True)
        self.base_model.fc = nn.Identity()

    """
     Defines the forward pass of the model. Input is passed through the base model 
     and then through the embedding layers.
     
     Args:
         x (Tensor): Input tensor containing image data.
     
     Returns:
         Tensor: Embedding output from the model.
     """
    def forward(self, x):
        # pass input through base and embedding layers
        x = self.base_model(x)
        x = self.embedding_layers(x)
        return x
