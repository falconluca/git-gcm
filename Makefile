.PHONY: install uninstall clean test help build clean-bin venv activate

BIN_DIR ?= ~/bin
VENV_DIR ?= .venv
PIP_INDEX_URL ?= https://pypi.tuna.tsinghua.edu.cn/simple

help:
	@echo "GCM - Git Commit Message Generator"
	@echo ""
	@echo "  make install    安装到本地（pip editable）"
	@echo "  make uninstall  卸载"
	@echo "  make clean      清理缓存"
	@echo "  make test       测试运行"
	@echo "  make rebuild    重新安装"
	@echo "  make build      打包二进制到 $(BIN_DIR)"
	@echo "  make clean-bin  清理二进制文件"
	@echo "  make venv       创建虚拟环境"
	@echo "  make activate   进入虚拟环境"

venv:
	@echo "创建虚拟环境..."
	python3 -m venv $(VENV_DIR)
	@echo "虚拟环境已创建: $(VENV_DIR)"
	@echo "运行 'source $(VENV_DIR)/bin/activate' 激活"

activate:
	@echo "进入虚拟环境..."
	@source $(VENV_DIR)/bin/activate && echo "已进入虚拟环境，输入 'exit' 退出" && $(SHELL)

install:
	pip install -e . -i $(PIP_INDEX_URL)

uninstall:
	pip uninstall -y gcm

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

test:
	@echo "测试 gcm 命令..."
	gcm --help

rebuild: clean install
	@echo "重新安装完成"

build:
	@echo "打包二进制文件..."
	pip install pyinstaller -q -i $(PIP_INDEX_URL)
	pyinstaller --onefile --name gcm gcm/cli.py
	install -m 755 dist/gcm $(BIN_DIR)/
	rm -rf build/ dist/ gcm.spec
	@echo "已安装到 $(BIN_DIR)/gcm"

clean-bin:
	@echo "清理二进制文件..."
	rm -rf build/ dist/ gcm.spec
	rm -f $(BIN_DIR)/gcm
	@echo "清理完成"
