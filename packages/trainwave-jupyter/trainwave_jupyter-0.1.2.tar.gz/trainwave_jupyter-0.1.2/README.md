# Trainwave Jupyter Extension

[![PyPI version](https://badge.fury.io/py/trainwave-jupyter.svg)](https://badge.fury.io/py/trainwave-jupyter)
[![npm version](https://badge.fury.io/js/trainwave-jupyter.svg)](https://badge.fury.io/js/trainwave-jupyter)

**Seamlessly run your Jupyter notebooks on powerful GPU infrastructure with Trainwave.ai**

The Trainwave Jupyter Extension brings the power of cloud GPU computing directly into your JupyterLab environment. Transform your notebooks into scalable GPU jobs with just a few clicks, without leaving your development environment.

## ✨ Features

- **🚀 One-Click Job Launch**: Convert notebooks to GPU jobs directly from the toolbar
- **🔐 Secure Authentication**: Integrated login with your Trainwave.ai account
- **📊 Real-time Job Monitoring**: Track job status and progress in real-time
- **⚙️ Flexible Configuration**: Customize GPU types, counts, and project settings
- **📱 Modern UI**: Clean, intuitive interface that integrates seamlessly with JupyterLab
- **🔄 Auto-save**: Automatically saves your notebook before launching jobs
- **📈 Job History**: View and manage your recent jobs from the extension

## 🎯 What is Trainwave.ai?

Trainwave.ai provides fast, cost-effective GPU computing for machine learning and data science workloads. With the Jupyter extension, you can:

- Run compute-intensive notebooks on powerful GPUs
- Scale your experiments without managing infrastructure
- Pay only for the compute time you use
- Access a variety of GPU types and configurations

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- JupyterLab 4.0 or higher

### Install from PyPI

```bash
pip install trainwave-jupyter
```

### Verify Installation

After installation, restart JupyterLab and look for the Trainwave icon in your notebook toolbar.

## 🚀 Quick Start

### 1. Sign In to Trainwave

1. Open a Jupyter notebook
2. Click the Trainwave icon in the toolbar
3. Click "Sign In" and authenticate with your Trainwave.ai account

### 2. Configure Your Settings

1. Click the settings icon in the Trainwave dropdown
2. Select your organization and project
3. Choose your preferred GPU type and count
4. Save your configuration

### 3. Launch Your First Job

1. Open or create a notebook with your code
2. Click the Trainwave icon in the toolbar
3. Click "Launch Job"
4. Enter a name for your job
5. Your notebook will be automatically saved and submitted to Trainwave

### 4. Monitor Your Jobs

- View active jobs in the Trainwave dropdown
- Click on job names to open them in the Trainwave web interface
- Jobs are automatically polled for status updates

## 📖 Detailed Usage

### Job Configuration

Configure your jobs through the settings dialog:

- **Organization & Project**: Select your workspace and project
- **GPU Type**: Choose from available GPU types (CPU, T4, V100, A100, etc.)
- **GPU Count**: Specify the number of GPUs for your job
- **Job Naming**: Customize job names or use automatic naming

### Job Management

- **Launch Jobs**: Convert any notebook to a GPU job
- **Monitor Status**: Real-time updates on job progress
- **Access Results**: Direct links to view jobs in the Trainwave web interface
- **Job History**: View recent jobs and their status

## 🔧 Configuration

### Environment Variables

You can configure the extension using environment variables:

```bash
export TRAINWAVE_API_ENDPOINT="https://backend.trainwave.ai"
export TRAINWAVE_POLLING_INTERVAL=10  # seconds
export TRAINWAVE_POLLING_TIMEOUT=300  # seconds
```

### JupyterLab Settings

Access extension settings through JupyterLab's settings system:

1. Go to Settings → Advanced Settings Editor
2. Select "Trainwave Jupyter Extension"
3. Modify configuration as needed

## 🛠️ Troubleshooting

### Extension Not Appearing

If you don't see the Trainwave icon in your notebook toolbar:

1. **Restart JupyterLab** after installation
2. **Check installation**:
   ```bash
   jupyter labextension list
   ```
3. **Manually enable** (if needed):
   ```bash
   jupyter serverextension enable --py trainwave-jupyter
   jupyter labextension enable trainwave-jupyter
   ```

### Authentication Issues

- **Clear browser cache** and try signing in again
- **Check network connectivity** to trainwave.ai
- **Verify API endpoint** in settings if using custom configuration

### Job Launch Failures

- **Check notebook path**: Ensure your notebook is saved
- **Verify settings**: Confirm organization and project are selected
- **Check API key**: Ensure you're properly authenticated
- **Review logs**: Check browser console for error messages

### Performance Issues

- **Reduce polling frequency** in settings for better performance
- **Close unused notebooks** to free up resources
- **Check network latency** to Trainwave servers

## 🆘 Support

- **Documentation**: [Trainwave.ai Documentation](https://trainwave.ai/docs)
- **Email**: [help@trainwave.ai](mailto:help@trainwave.ai)

## 🔗 Links

- **Website**: [trainwave.ai](https://trainwave.ai)
- **Documentation**: [trainwave.ai/docs](https://trainwave.ai/docs)
- **Dashboard**: [trainwave.ai/jobs](https://trainwave.ai/jobs)
