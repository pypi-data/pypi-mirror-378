import torch
from typing import Optional, Dict
import logging
from torch.utils.data import DataLoader
from diresa_torch.arch.models import Diresa
from operator import add

# TODO: Could improve visual feedback for training use tqdm


def __compute_losses(outputs, targets, criterions, loss_weights):
    """
    Helper function to compute losses given outputs, targets, criterions and weights.

    :param outputs: Model outputs (tuple of 3 elements: reconstructed, latent, distance)
    :param targets: Target values (tuple of 3 elements: data, None, None)
    :param criterions: List of loss functions [ReconstructionLoss, CovarianceLoss, DistanceLoss]
    :param loss_weights: Weighting factor for the different losses
    :return: Tuple of (individual_losses, total_weighted_loss)
    """
    individual_losses = [c(o, t) for c, o, t in zip(criterions, outputs, targets)]
    weighted_losses = [w * l for w, l in zip(loss_weights, individual_losses)]
    total_weighted_loss = torch.stack(weighted_losses).sum()

    return individual_losses, total_weighted_loss


def __set_non_trainable(model):
    for param in model.parameters():
        param.requires_grad = False


def __evaluate(
    produce_output: callable,
    produce_target: callable,
    test_loader: DataLoader,
    criterions: list,
    device: str = 'cpu',
    loss_weights: list = [1., 1., 1.]
) -> Dict[str, float]:
    """
    Evaluate DIRESA (does not track gradient) by computing all three losses (reconstruction, covariance, distance)
    with help of the ``produce_output`` and ``produce_input`` functions. Those functions are provided as lambdas
    which makes it easier to match the outputs, targets and criterions together for evaluation purposes.

    :param produce_output: callable function producing outputs from model. Takes as input batch data.
    :param produce_target: callable function producing target values for criterion. Takes as input batch data.
    :param test_loader: Test data loader
    :param criterions: List of loss functions, depends on what part is being evaluated.
    :param device: Device to evaluate on
    :param loss_weights: Weighting factor for the different losses

    :return: Dictionary with average losses: individual losses + weighted total loss
    """
    total_losses = [0.0] * (len(criterions) + 1)
    num_batches = 0

    loss_names = [f"{c}"[:-2] for c in criterions] + ['WeightedLoss']

    with torch.no_grad():
        for _, data in enumerate(test_loader):
            data = data.to(device)

            outputs = produce_output(data)

            targets = produce_target(data)

            # outputs_losses, loss = _compute_losses(outputs, target, criterions, loss_weights)
            outputs_losses, loss = __compute_losses(
                outputs, targets, criterions, loss_weights)

            # Accumulate losses
            all_losses = outputs_losses + [loss]
            total_losses = list(
                map(add, total_losses, [loss.item() for loss in all_losses]))
            num_batches += 1

    avg_losses = [loss / num_batches for loss in total_losses]

    result = {name: avg_loss for name, avg_loss in zip(loss_names, avg_losses)}

    return result


def train_diresa(
    model: Diresa,
    train_loader: DataLoader,
    criterions: list,
    optimizer: torch.optim.Optimizer,
    num_epochs: int = 10,
    device: str = 'cpu',
    val_loader: Optional[DataLoader] = None,
    callbacks: Optional[list] = None,  # Not IMPL at the moment -> see assert
    loss_weights: list = [1., 1., 1.],
    staged_training: bool = False
) -> Dict[str, list]:
    """
        Trains DIRESA.

        :param model: The model to train
        :param train_loader: Training data loader
        :param criterion: List of Loss function. With order [ReconstructionLoss, CovarianceLoss, DistanceLoss]
        :param optimizer: Optimizer
        :param num_epochs: Number of epochs
        :param device: Device to train on
        :param val_loader: Optional validation loader
        :param callbacks: Optional list of callback functions
        :param loss_weights: Weighting factor for the different losses.
        :param staged_trainig: If set to True will train the encoder and the decoder separately for ``num_epochs`` each.

        :return Dict with training (losses, metrics) and validation (if val_loader is provided).
    """
    assert callbacks is None, "Callbacks are not tested at the moment. Remove param or set to None"

    def __train_for_epochs(produce_output: callable, produce_target: callable, criterions, loss_weights, prepend_log="DIRESA"):
        """
            Nested function for training loop. Factors out common functionalities for training,
            while providing custom informations about what loss to train for used to differentiate
            between staged training and full training.

            :param produce_output: callable function producing outputs from model. Takes as input batch data.
            :param produce_target: callable function producing target values for criterion. Takes as input batch data.
            :param criterions: List of loss functions
            :param loss_weights: weights for each loss function
            :param prepend_log: String to prepend to logging output
        """
        assert len(criterions) == len(
            loss_weights), "Number of criterions and their associated weights does not match"

        # Ordering of loss ouput values
        # Use class name without the last () as name for the loss
        loss_names = [f"{c}"[:-2] for c in criterions] + ['WeightedLoss']

        # add "train" suffix for output
        train_loss_names = list(map(lambda x: x + "_train", loss_names))
        history = {loss_name: [] for loss_name in train_loss_names}

        for epoch in range(num_epochs):
            # each criterion loss + combined weighted loss
            epoch_loss = [0.0] * (len(criterions) + 1)
            num_batches = 0

            for batch_idx, data in enumerate(train_loader):

                data = data.to(device)
                target = produce_target(data)
                outputs = produce_output(data)

                optimizer.zero_grad()
                outputs_losses, loss = __compute_losses(
                    outputs, target, criterions, loss_weights)

                # accumulates gradient in each tensor -> Backprop
                # backpropagated loss in weighted sum of each loss.
                loss.backward()

                optimizer.step()

                # add weighted loss to final losses
                all_losses = outputs_losses + [loss]
                epoch_loss = list(map(add, epoch_loss, [loss.item() for loss in all_losses]))
                num_batches += 1

                if callbacks:
                    for callback in callbacks:
                        callback(epoch, batch_idx, loss.item())

            avg_loss = list(map(lambda loss: loss / num_batches, epoch_loss))

            for k, value in zip(train_loss_names, avg_loss):
                history[k].append(value)

            # val loader is defined in exterior function
            if val_loader:
                val_dict = __evaluate(
                    produce_output,
                    produce_target,
                    val_loader,
                    criterions,
                    device,
                    loss_weights
                )
                renamed_val = {f"{k}_val": v for k, v in val_dict.items()}
                for k, value in renamed_val.items():
                    if k in history:
                        history[k].append(value)
                    else:
                        history[k] = [value]

            # print out last entry in history for each epoch
            log_str = ", ".join(
                [f"{name}: {values[-1]:.4e}" for name, values in history.items()])
            logging.info(
                f'{prepend_log}: Epoch {epoch + 1}/{num_epochs} - {log_str}')

        return history

    # End of nested function

    model: Diresa = model.to(device)

    if staged_training:
        # train encoder, cov and dist loss
        hist_encoder = __train_for_epochs(
            lambda data: model._encode_with_distance(data.x),
            lambda data: (None, None),
            criterions[1:],  # cov and dist criterions
            loss_weights[1:],  # cov and dist weights
            prepend_log="Encoder"
        )

        # freeze encoder weights
        __set_non_trainable(model.base_encoder)

        # train decoder, only rec loss
        hist_decoder = __train_for_epochs(
            lambda data: model.base_decoder(model.base_encoder(data.x)),
            lambda data: data.y,
            criterions[:1],
            loss_weights[:1],
            prepend_log="Decoder"
        )

        hist = {**hist_encoder, **hist_decoder}
        return hist

    else:
        # data is produced by forward pass of model.
        hist = __train_for_epochs(
            lambda data: model(data.x),
            lambda data: (data.y, None, None),
            criterions,
            loss_weights
        )

        return hist


def evaluate_diresa(
    model: Diresa,
    test_loader: DataLoader,
    criterions: list,
    device: str = 'cpu',
    loss_weights: list = [1., 1., 1.]
) -> Dict[str, float]:

    assert len(criterions) == 3, "Need to provide 3 criterions for DIRESA evaluation, namely [DistanceLoss, CovarianceLoss, DistanceLoss]"

    eval_dict = __evaluate(
        # model.forward(data) produces (reconstruced, latent, dist)
        lambda data: model.forward(data.x),
        lambda data: (data.y, None, None),
        test_loader=test_loader,
        criterions=criterions,
        device=device,
        loss_weights=loss_weights
    )
    log_str = ", ".join(
        [f"{name}_eval: {value:.4e}" for name, value in eval_dict.items()])
    logging.info(log_str)
    return eval_dict


def predict_diresa(
    model: Diresa,
    data_loader: DataLoader,
    device: str = 'cpu'
) -> torch.Tensor:
    """
    Generate predictions for DIRESA using a trained model
    Provides faster inference as it does not compute distance or covariance losses.
    """
    model: Diresa = model.to(device)

    predictions = []

    with torch.no_grad():
        for _, data in enumerate(data_loader):
            data = data.to(device)
            outputs = model.fast_eval(data)
            predictions.append(outputs.cpu())

    return torch.cat(predictions, dim=0)
