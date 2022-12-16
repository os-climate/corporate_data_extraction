import optuna
import model_pipeline
from model_pipeline import FARMTrainer, ModelConfig, FileConfig, TokenizerConfig, MLFlowConfig, ProcessorConfig, TrainingConfig

def objective(trial):
    # Uniform parameter
    dropout_rate = trial.suggest_uniform('dropout_rate', 0.0, 1.0)

    num_epochs = trial.suggest_int('num_epochs', 1, 5, 1)
    batch_size = trial.suggest_int('batch_size', 4, 32, 4)

    # Loguniform parameter
    learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)

    file_config = FileConfig()
    train_config = TrainingConfig()

    train_config.learning_rate = learning_rate
    train_config.n_epochs = num_epochs
    train_config.dropout = dropout_rate
    train_config.batch_size = batch_size
    train_config.run_hyp_tuning = True

    model_config = ModelConfig()
    mlflow_config = MLFlowConfig()
    processor_config = ProcessorConfig()
    tokenizer_config = TokenizerConfig()

    farm_trainer = FARMTrainer(
            file_config =file_config,
            tokenizer_config=tokenizer_config,
            model_config=model_config,
            processor_config=processor_config,
            training_config=train_config,
            mlflow_config=mlflow_config
        )
    acc = farm_trainer.run(trial)

    return acc

if __name__ == "__main__":
    study = optuna.create_study(direction="maximize", pruner=optuna.pruners.MedianPruner())
    study.optimize(objective, n_trials=100)

    pruned_trials = [t for t in study.trials if t.state == optuna.structs.TrialState.PRUNED]
    complete_trials = [t for t in study.trials if t.state == optuna.structs.TrialState.COMPLETE]

    print("Study statistics: ")
    print("  Number of finished trials: ", len(study.trials))
    print("  Number of pruned trials: ", len(pruned_trials))
    print("  Number of complete trials: ", len(complete_trials))

    print("Best trial:")
    trial = study.best_trial

    print("  Value: ", trial.value)

    print("  Params: ")
    for key, value in trial.params.items():
        print("    {}: {}".format(key, value))
