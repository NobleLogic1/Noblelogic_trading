@echo off
REM Set environment variable to disable heavy TensorFlow/Transformers initialization
REM This speeds up import times significantly

REM Disable TensorFlow oneDNN optimizations (reduces startup time)
set TF_ENABLE_ONEDNN_OPTS=0

REM Disable TensorFlow CUDA initialization warnings
set TF_CPP_MIN_LOG_LEVEL=2

REM Set transformers cache to local directory
set TRANSFORMERS_CACHE=./cache/transformers

REM Disable transformers telemetry
set HF_HUB_DISABLE_TELEMETRY=1

echo Environment optimizations applied for faster startup!