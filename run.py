#!/usr/bin/env python3
from app import app
import os

port = os.environ.get('PORT', 5380)

if __name__ == '__main__':
    app.run(port=port, host='0.0.0.0', debug=True)

