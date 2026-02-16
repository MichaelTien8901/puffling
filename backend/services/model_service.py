MODEL_TYPES = {
    "ml": {
        "trading_model": "puffin.ml.TradingModel",
    },
    "ensembles": {
        "random_forest": "puffin.ensembles.RandomForestTrader",
        "xgboost": "puffin.ensembles.XGBoostTrader",
        "lightgbm": "puffin.ensembles.LightGBMTrader",
        "catboost": "puffin.ensembles.CatBoostTrader",
    },
    "deep": {
        "ffn": "puffin.deep.TradingFFN",
        "lstm": "puffin.deep.TradingLSTM",
        "gru": "puffin.deep.TradingGRU",
        "cnn": "puffin.deep.TradingCNN",
    },
    "rl": {
        "q_learning": "puffin.rl.QLearningAgent",
        "dqn": "puffin.rl.DQNAgent",
        "ppo": "puffin.rl.PPOTrader",
    },
}


class ModelService:
    def list_types(self) -> dict:
        return {category: list(models.keys()) for category, models in MODEL_TYPES.items()}

    def train(self, model_type: str, params: dict) -> dict:
        for category, models in MODEL_TYPES.items():
            if model_type in models:
                module_path = models[model_type]
                parts = module_path.rsplit(".", 1)
                mod = __import__(parts[0], fromlist=[parts[1]])
                cls = getattr(mod, parts[1])
                instance = cls(**params.get("model_params", {}))
                if hasattr(instance, "fit"):
                    result = instance.fit(params.get("X"), params.get("y"))
                    return {"model_type": model_type, "status": "trained", "result": str(result)}
                elif hasattr(instance, "train"):
                    result = instance.train(**params.get("train_params", {}))
                    return {"model_type": model_type, "status": "trained", "result": str(result)}
                return {"model_type": model_type, "status": "instantiated"}
        raise ValueError(f"Unknown model type: {model_type}")

    def predict(self, model_type: str, params: dict) -> dict:
        return {"model_type": model_type, "predictions": [], "status": "not_implemented"}
