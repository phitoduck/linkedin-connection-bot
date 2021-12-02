#!/bin/bash

function make-run() {
    python src/linkedin_bot/main.py
}

function make-run-docker() {
    docker-compose run linkedin-bot
}

function make-install() {
    python -m pip install "."
}

function make-build-image() {
    docker-compose build
}

eval "make-$1"