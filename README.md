# Serverless ML Core service

Core service for serverless ML training/serving

## Modus Operandi

### Train

1. Upon invocation, validate input config

```javascript
    {
        "run_id": String ("UUID4"),
        "code_hash": String("SHA1"),
        "pipeline_config": {
            "data": {
                "location": {
                    "source": "DATA/SAMPLE/LOCATION",
                },
                "prep_config": Object,
            },
            "model": {
                "hyperparameters": {
                    "param1": Number,
                    "param2": String,
                    "param3": Number,
                },
                "version": "MODEL/VERSION/IN/PACKAGE",
            },
        },
    }
```

2. Instantiate `model` class
3. Read data sample into memory
4. Perform model training
5. Save model
6. Push notification to the topic


### Predict

#### Batch prediction

1. Upon invocation, validate input config

```javascript
    {
        "run_id": String ("UUID4"),
        "pipeline_config": {
            "train_id": String ("UUID4"),
            "data": {
                "location": {
                    "source": "DATA/SAMPLE/LOCATION",
                    "destination": "DATA/SAMPLE/LOCATION",
                },
            },
        }.
    }
```

1. Read model metadata
2. Instantiate `model` class
3. Read dataset
4. Run prediction
5. Output results

#### Web-server

Deployed separately, with the fixed model.
