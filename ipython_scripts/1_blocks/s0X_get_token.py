# %% [markdown]

# <p><center>Ocean Protocol</p>
# <p><center>Trilobite pre-release 0.1</center></p>
# <img src="https://oceanprotocol.com/static/media/logo-white.7b65db16.png" alt="drawing" width="200" align="center"/>
# </center>

# %%
# Ocean Protocol
#
# Trilobite release
#
# <img src="https://oceanprotocol.com/static/media/logo-white.7b65db16.png" alt="drawing" width="200"/>
# <img src="https://oceanprotocol.com/static/media/logo.75e257aa.png" alt="drawing" width="200"/>
#
# %% [markdown]
# # Test functionality of squid-py wrapper.

# %% [markdown]
# <img src="https://3c1703fe8d.site.internapcdn.net/newman/gfx/news/hires/2017/mismatchedey.jpg" alt="drawing" width="200" align="center"/>

# %% [markdown]
# ## Section 1: Import modules, and setup logging

# %% [markdown]
# Imports
#%%
from pathlib import Path
import squid_py.ocean as ocean_wrapper
# from squid_py.utils.web3_helper import convert_to_bytes, convert_to_string, convert_to_text, Web3Helper
import sys
import random
import json
import os
from pprint import pprint
import configparser
# import squid_py.ocean as ocean
from squid_py.ocean.ocean import Ocean
from squid_py.ocean.asset import Asset
import names
import secrets
from squid_py.ddo import DDO
from unittest.mock import Mock
import squid_py
print(squid_py.__version__)
import unittest

# %% [markdown]
# Logging
# %%
import logging
loggers_dict = logging.Logger.manager.loggerDict
logger = logging.getLogger()
logger.handlers = []
# Set level
logger.setLevel(logging.INFO)
FORMAT = "%(levelno)s - %(module)-15s - %(funcName)-15s - %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(FORMAT, DATE_FMT)
# Create handler and assign
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(formatter)
logger.handlers = [handler]
logger.info("Logging started")
# %% [markdown]
# ## Section 2: Instantiate the Ocean Protocol interface

#%%
# The contract addresses are loaded from file
# CHOOSE YOUR CONFIGURATION HERE
PATH_CONFIG = Path.cwd() / 'config_local.ini'
assert PATH_CONFIG.exists(), "{} does not exist".format(PATH_CONFIG)

ocn = Ocean(PATH_CONFIG)
logging.info("Ocean smart contract node connected ".format())

# Passwords for simulated accounts can be hardcoded here
PASSWORD_MAP = {
    '0x00bd138abd70e2f00903268f3db08f2d25677c9e' : 'node0',
    '0x068ed00cf0441e4829d9784fcbe7b9e26d4bd8d0' : 'secret',
    '0xa99d43d86a0758d5632313b8fa3972b6088a21bb' : 'secret',
}

# %% [markdown]
# ## Section 3: Users and accounts
# %% [markdown]
# List the accounts created
#%%

# ocn.accounts is a {address: Account} dict
for address in ocn.accounts:
    acct = ocn.accounts[address]
    print(acct.address)

#%%
# These accounts have a positive or 0 balance
for address, account in ocn.accounts.items():
    assert account.balance.eth >= 0
    assert account.balance.ocn >= 0

# %% [markdown]
# Get funds to users
# A simple wrapper for each address is created to represent a User
# A User has a Name, a Role, and an address
#
# Users are instantiated and listed

#%%
class User():
    def __init__(self, name, role, address, config_path=None):
        self.name = name
        self.address = address
        self.role = role
        self.locked = True
        self.config_path = config_path

        self.ocn = None
        self.account = None

        # If the account is unlocked, instantiate Ocean and the Account classes
        if self.address.lower() in PASSWORD_MAP:
            password = PASSWORD_MAP[self.address.lower()]

            # The ocean class REQUIRES a .ini file -> need to create this file!
            if not self.config_path:
                self.config_fname = "{}_{}_config.ini".format(self.name,self.role).replace(' ', '_')
                config_path = self.create_config(password) # Create configuration file for this user

            # Instantiate Ocean and Account for this User
            self.ocn = Ocean(config_path)
            self.unlock(password)
            acct_dict_lower = {k.lower(): v for k, v in ocn.accounts.items()}
            self.account = acct_dict_lower[self.address.lower()]

            cleanup=True # Delete this temporary INI
            if cleanup:
                config_path.unlink()

        logging.info(self)

    def unlock(self, password):
        self.ocn._web3.personal.unlockAccount(self.address, password)
        self.locked = False

    def create_config(self,password):
        conf = configparser.ConfigParser()
        conf.read(PATH_CONFIG)
        conf['keeper-contracts']['parity.address'] = self.address
        conf['keeper-contracts']['parity.password'] = password
        out_path = Path.cwd() / 'user_configurations' / self.config_fname
        print(out_path)
        with open(out_path, 'w') as fp:
            conf.write(fp)
        return out_path

    def __str__(self):
        if self.locked:
            return "{:<20} {:<20} LOCKED ACCOUNT".format(self.name, self.role)
        else:
            ocean_token = self.account.ocean_balance
            return "{:<20} {:<20} with {} Ocean token".format(self.name, self.role, ocean_token)

    def __repr__(self):
        return self.__str__()


#%% Create the users, one per simulated address
users = list()
for i, acct_address in enumerate(ocn.accounts):
    if i%2 == 0: role = 'Data Scientist'
    else: role = 'Data Owner'
    user = User(names.get_full_name(), role, acct_address)
    users.append(user)

# Select only unlocked accounts going forward
users = [u for u in users if not u.locked]


#%% [markdown]
# List the users

#%%
for u in users: print(u)

#%% [markdown]
# Get some Ocean token
#%%
for usr in users:
    if usr.account.ocean_balance == 0:
        rcpt = usr.account.request_tokens(random.randint(0,100))
        usr.ocn._web3.eth.waitForTransactionReceipt(rcpt)

for u in users: print(u)
