#!/usr/bin/env python3
"""
Database connection management for Smart Chart RAG System
Handles Oracle database connections
"""

import oracledb
import streamlit as st
from config.settings import DB_CONFIG


def get_connection():
    """Get Oracle database connection"""
    try:
        connection = oracledb.connect(
            user=DB_CONFIG["username"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            service_name=DB_CONFIG["service_name"],
        )
        return connection
    except Exception as e:
        if "st" in globals():
            st.error(f"❌ Error connecting to Oracle database: {e}")
        else:
            print(f"❌ Error connecting to Oracle database: {e}")
        return None


def test_connection():
    """Test database connection and return status"""
    try:
        connection = get_connection()
        if not connection:
            return False, "Failed to establish connection"

        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection test failed: {e}"


def close_connection(connection):
    """Safely close database connection"""
    if connection:
        try:
            connection.close()
        except Exception as e:
            if "st" in globals():
                st.warning(f"Warning: Error closing connection: {e}")
            else:
                print(f"Warning: Error closing connection: {e}")
