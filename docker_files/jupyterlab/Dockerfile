# 使用官方JupyterLab镜像作为基础
FROM jupyter/base-notebook:latest

# 设置工作目录
WORKDIR /home/jovyan

# 安装Python数据科学库和JupyterLab扩展
RUN conda install --quiet --yes \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    statsmodels \
    jupyterlab \
    && conda clean --all -f -y

# 安装量化分析库，如TA-Lib等
RUN conda install -c conda-forge ta-lib

# 安装其他你可能需要的库
# RUN pip install some-other-library

# 为了方便调试，设置JupyterLab的密码（这里设置为'allan'）
RUN echo "from jupyter_server.auth import passwd; c.NotebookApp.password = passwd('allan')" > /home/jovyan/.jupyter/jupyter_notebook_config.py

# 暴露JupyterLab端口
EXPOSE 8081

# 启动JupyterLab
CMD ["jupyter", "lab", "--ip='0.0.0.0'", "--port=8081", "--no-browser", "--allow-root"]
