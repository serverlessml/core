# Serverless ML Core service

Core service for serverless ML training/serving

## Modus Operanti

### Training

1. Upon invocation, validate input config

```javascript
    {
        "data": {
            "location": "DATA/SAMPLE/LOCATION",
        },
        "model": {
            "hyperparameters": {
                "param1": Number,
                "param2": String,
                "param3": Number,
            },
            "version": "MODEL/VERSION/IN/PACKAGE",
        }
    }
```

2. Instantiate `model` class
3. Read datasample into memory
4. Perform model training
5. Save model
6. Push notification to the topic


### Serving

##### Batch prediction

1. Upon invocation, validate input config

```javascript
    {
        "code_hash": "codebase git hash",
        "data": {
            "location": {
                "source": "DATA/SAMPLE/LOCATION"
            },
        },
        "model": {
            "hyperparameters": {
                "param1": Number,
                "param2": String,
                "param3": Number,
            },
            "version": "MODEL/VERSION/IN/PACKAGE",
        }
    }
```

or

```javascript
    {
        "code_hash": "codebase git hash",
        "data": {
            "location": {
                "source": "DATA/SAMPLE/LOCATION",
                "destination": "DATA/SAMPLE/LOCATION",
            },
        },
        "model": {
            "runID": "MODEL/VERSION/IN/PACKAGE",
        }
    }
```

2. Read model metadata
3. Instantiate `model` class
4. Read dataset
5. Run prediction
6. Output results

##### Web-server

Deployed separately, with the fixed model.
