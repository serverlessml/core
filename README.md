# Serverless ML Core service

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue.svg)](https://pypi.org/project/kedro/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/ambv/black)
![Build](https://github.com/serverlessml/core/workflows/Build/badge.svg?branch=master)

Core service for serverless ML training/serving


## Modus Operandi

### Train

1. Upon invocation, validate input config

```javascript
    {
        "project_id": String ("UUID4, ML project ID"),
        "run_id": String ("UUID4, ML experiment ID"),
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
        "project_id": String ("UUID4, ML project ID"),
        "run_id": String ("UUID4, pipeline run ID"),
        "pipeline_config": {
            "train_id": String ("UUID4, ML experiment ID"),
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
