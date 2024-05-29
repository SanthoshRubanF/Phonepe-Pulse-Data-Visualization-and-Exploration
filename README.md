# Phonepe Pulse Data Visualization and Exploration: A User-Friendly Tool Using Streamlit and Plotly

## Overview

This project aims to visualize and explore data from PhonePe, a digital payments platform in India. It involves analyzing various aspects of transactions, insurance, and user behavior over time.

## Required Packages

- `json`
- `streamlit`
- `pandas`
- `requests`
- `psycopg2`
- `plotly`
- `streamlit_option_menu`

## SQL Connection and Data Retrieval

The data is stored in a PostgreSQL database. Using `psycopg2`, we establish a connection to the database and retrieve relevant tables for analysis.

## Functions for Data Analysis and Visualization

This section contains functions for performing aggregated analysis, map analysis, and top analysis on the retrieved data.

## Streamlit Application

The core logic of the application is implemented using Streamlit. It provides an interactive interface for exploring the data.

## Exploration Sections

### Aggregated Analysis

#### Insurance Analysis

This section allows users to visualize aggregated insurance data over different time periods.

#### Transaction Analysis

Users can analyze aggregated transaction data based on selected parameters like year, quarter, and state.

#### User Analysis

Provides insights into user behavior by visualizing aggregated user data.

### Map Analysis

#### Map Insurance Analysis

Visualize insurance data on a map, allowing users to explore geographic trends.

#### Map Transaction Analysis

Map-based visualization of transaction data helps identify regional transaction patterns.

#### Map User Analysis

Analyze user data geographically to understand user distribution and behavior across different regions.

### Top Analysis

#### Top Insurance Analysis

Identify top insurance trends based on selected parameters like year.

#### Top Transaction Analysis

Discover top transaction trends over time.

#### Top User Analysis

Identify top users based on selected criteria such as transaction count or amount.

