# 使用官方JupyterLab镜像作为基础
FROM jupyter/base-notebook:latest

# 设置工作目录
WORKDIR /home/jovyan

# 设置conda的源为TUNA
USER root
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
 && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
 && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/ \
 && conda config --set show_channel_urls yes

# 安装Python数据科学库和JupyterLab扩展
RUN conda install --quiet --yes \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    statsmodels \
    jupyterlab \
    pymongo\
    && conda clean --all -f -y

# 安装量化分析库
RUN conda install -c conda-forge ta-lib 

# 安装其他你可能需要的库
RUN pip install tushare backtrader

RUN apt-get update && apt-get install -y vim curl unzip fontconfig 

# 为 'jovyan' 用户添加无密码 sudo 权限
RUN echo "jovyan ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/jovyan && \
    chmod 0440 /etc/sudoers.d/jovyan

COPY oh-my-zsh-p10k.sh /home/jovyan/
COPY MesloLGS_NF_Regular.ttf MesloLGS_NF_Bold.ttf MesloLGS_NF_Italic.ttf MesloLGS_NF_Bold_Italic.ttf  /usr/share/fonts/truetype/MesloLGS_NF/
RUN fc-cache -fv

RUN chmod +x /home/jovyan/oh-my-zsh-p10k.sh
RUN /home/jovyan/oh-my-zsh-p10k.sh
COPY p10k.zsh /home/jovyan/.p10k.zsh
COPY zshrc /home/jovyan/.zshrc

RUN git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
RUN chown -R jovyan:users /home/jovyan

RUN ~/.fzf/install --all
# 切换回 jovyan 用户
USER jovyan
# 为了方便调试，设置JupyterLab的密码（这里设置为'allan'）
RUN echo "from jupyter_server.auth import passwd; c.NotebookApp.password = passwd('allan')" > /home/jovyan/.jupyter/jupyter_notebook_config.py

# 设置JupyterLab
EXPOSE 8081
CMD ["jupyter", "lab", "--ip='0.0.0.0'", "--port=8081", "--no-browser", "--allow-root"]