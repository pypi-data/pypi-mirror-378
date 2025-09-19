#!/usr/bin/env python
# Script            : To verify the token coming in the request with the token from Redis. (Encryption and Decryption are included)
# Component         : GenAi Extraction Validate API
# Author            : Vinay Namani & Anuja Fole
# Copyright (c)     : 2023 Katonic Pty Ltd. All rights reserved.


# -----------------------------------------------------------------------------
#                        necessary Imports
# -----------------------------------------------------------------------------

# imports
import os
import json

# from loguru import logger
from routes.utilities.logutils import Logger
from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from fastapi.security.utils import get_authorization_scheme_param
from db_init import Redis

logger = Logger(f"/opt/log_files/token_verify")

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
run_id = "8eed07eef46f4282b81b5090b649447fkatonic"
deployment_id = os.environ["APP_NAME"].split("-")[-1]

redisDB = Redis(1)


async def verify_token(req: Request):
    """
    Method to verify the token receiving from the request against the token in Redis Database.
    Args:
        req: Request object which consists of a header 'Authorization' which contains the token.
    """
    authorization: str = req.headers.get("Authorization")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "None"},
    )
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token",
    )
    if not authorization:
        raise credentials_exception
    if len(authorization.split()) != 2:
        raise token_exception
    ##TODO: define the token for this
    if authorization == os.environ["TEST_API_TOKEN"]:
        logger.info("Request source: KatonicGENAI Platform UI")
    else:
        logger.info("Request source: Model API Endpoint")
        logger.info(f"Retriving Authorization Header Value")
        scheme, param = get_authorization_scheme_param(authorization)

        logger.info("Getting Database response")
        redis_response = redisDB.get(scheme)

        if not redis_response:
            logger.info(f"No key present in DB with scheme : {scheme}")
            raise token_exception
        logger.info("Successfully retrieved Database Response")

        if "accessToken" in redis_response:
            par_dict = json.loads(redis_response)
            token = par_dict["accessToken"]
        else:
            token = redis_response
        logger.info("Retrieved token from Database response")

        if param != token:
            logger.info("token does not match")
            raise token_exception
        try:
            logger.info("Decoding the token")
            payload = jwt.decode(param, SECRET_KEY, algorithms=[ALGORITHM])
            logger.info("Token decoded successfully")
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token expired",
            ) from e
        payload_run_id: str = payload.get("sub")

        logger.info("Sucessfully retrieved unique_id")

        if payload_run_id != deployment_id + "-" + run_id:
            logger.info("Token does not match")
            raise token_exception
        logger.info("Token Authorization Successful")
