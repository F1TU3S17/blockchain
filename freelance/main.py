from api import API
from PyQt5 import QtWidgets

from ok import Ui_isOk
from regLog import Ui_reg
from run import Ui_MainWindow
from history import Ui_tasksHistory
import sys


class User:
    def __init__(self, account_address, nickname):
        self.account_address = str(account_address)
        self.nickname = str(nickname)


class Ok(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_isOk()
        self.ui.setupUi(self)
        self.ui.okBtn.clicked.connect(self.close)

class HistoryWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_tasksHistory()
        self.ui.setupUi(self)

class RegLog(QtWidgets.QDialog):
    api = API()

    def __init__(self):
        super().__init__()
        self.ui = Ui_reg()
        self.ui.setupUi(self)
        self.ui.logButton.clicked.connect(self.login)
        self.ui.regButton.clicked.connect(self.registration)
    def login(self):
        login = str(self.ui.logLogin.text())
        pwd = str(self.ui.logPwd.text())
        result = self.api.login(login, pwd)
        if result:
            self.close()
            user = User(login, self.api.get_user_nickname(login))
            self.open = Main(user)
            self.open.show()
        else:
            self.eBar = QtWidgets.QErrorMessage()
            self.eBar.setWindowTitle('Ошибка')
            self.eBar.showMessage("Неправильный логин или пароль")

    def registration(self):
        nickname = str(self.ui.regNick.text())
        login = str(self.ui.regLogin.text())
        pwd = str(self.ui.regPwd.text())
        result = self.api.registration(nickname, login, pwd)
        if result:
            self.close()
            user = User(login, nickname)
            self.open = Main(user)
            self.open.show()
        else:
            self.eBar = QtWidgets.QErrorMessage()
            self.eBar.setWindowTitle('Ошибка')
            self.eBar.showMessage('Пользователь под данным адресом или ником существует')

class Main(QtWidgets.QMainWindow):
    api = API()
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.eBar = QtWidgets.QErrorMessage()
        self.eBar.setWindowTitle('Ошибка!!!')
        self.ok = Ok()
        self.ui.balanceLabel.setText((str(self.api.get_balance(self.user.account_address)) + " wei"))
        self.ui.customerHistoryButton.clicked.connect(self.open_customer_history_window)
        self.ui.executorHistoryButton.clicked.connect(self.open_executor_history_window)
        self.ui.accountNick.setText(user.nickname)
        self.ui.accountAddress.setText(user.account_address)
        self.tasks_in_search_table()
        self.ui.taskToWorkButton.clicked.connect(self.get_task_to_work)
        self.ui.addTask.clicked.connect(self.add_new_task)
        self.ui.myTaskInWork.clicked.connect(self.get_my_task_in_work_table)
        self.ui.taskStatusGood.clicked.connect(self.good_status_my_work)
        self.ui.taskStatusBad.clicked.connect(self.bad_status_my_work)
        self.ui.myZakazi.clicked.connect(self.get_my_zakaz_in_table)
        self.ui.taskStatusGoodZ.clicked.connect(self.good_status_my_z)
        self.ui.taskStatusBadZ.clicked.connect(self.bad_status_my_z)

    def open_customer_history_window(self):
        self.open = HistoryWindow()
        self.open.show()
        customer_history_list = self.api.customer_history(self.user.account_address)
        customer_history_list = self.api.transform_all_info_to_ui(customer_history_list)
        self.open.ui.tableWidget.setRowCount(len(customer_history_list))
        for i in range(len(customer_history_list)):
            for j in range(len(customer_history_list[i])):
                self.open.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(customer_history_list[i][j])))

    def open_executor_history_window(self):
        self.open = HistoryWindow()
        self.open.show()
        executor_history_list = self.api.executor_history(self.user.account_address)
        executor_history_list = self.api.transform_all_info_to_ui(executor_history_list)
        self.open.ui.tableWidget.setRowCount(len(executor_history_list))
        for i in range(len(executor_history_list)):
            for j in range(len(executor_history_list[i])):
                self.open.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(executor_history_list[i][j])))

    def tasks_in_search_table(self):
        tasks = self.api.get_all_tasks_in_search()
        tasks_len = len(tasks)
        self.ui.tableWidget.setRowCount(tasks_len)
        for i in range(0, tasks_len):
            for j in range(0, len(tasks[i])):
                self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(tasks[i][j])))

    def get_task_to_work(self):
        try:
            task_id = int(self.ui.lineTaskId.text())
            isInWork = self.api.task_to_work(self.user.account_address, task_id)
            if isInWork:
                self.ok.show()
                self.tasks_in_search_table()
            else:
                self.eBar.showMessage(f'Задача не взята в работу, т.к либо занята, либо не существует либо это ваша задача')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def add_new_task(self):
        try:
            task_title = str(self.ui.lineTaskTitle.text())
            task_price = int(self.ui.lineTaskPrice.text())
            task_describe = str(self.ui.textTaskDescribe.toPlainText())
            print(task_describe)
            is_add = self.api.add_task(self.user.account_address, task_price, task_title, task_describe)
            if is_add:
                self.tasks_in_search_table()
                self.ok.show()
            else:
                self.eBar.showMessage(f'Не удалось добавить задачу')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def get_my_task_in_work_table(self):
        try:
            self.open = HistoryWindow()
            self.open.show()
            executor_list = self.api. task_to_execute(self.user.account_address)
            executor_list = self.api.transform_all_info_to_ui(executor_list)
            self.open.ui.tableWidget.setRowCount(len(executor_list))
            for i in range(len(executor_list)):
                for j in range(len(executor_list[i])):
                    self.open.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(executor_list[i][j])))
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def get_my_zakaz_in_table(self):
        try:
            self.open = HistoryWindow()
            self.open.show()
            customer_tasks = self.api.customer_tasks(self.user.account_address)
            customer_tasks = self.api.transform_all_info_to_ui(customer_tasks)
            self.open.ui.tableWidget.setRowCount(len(customer_tasks))
            for i in range(len(customer_tasks)):
                for j in range(len(customer_tasks[i])):
                    self.open.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(customer_tasks[i][j])))
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')
    def good_status_my_work(self):
        try:
            task_id = str(self.ui.lineTaskStatusId.text())
            is_changed = self.api.set_task_to_done(self.user.account_address, task_id)
            if is_changed:
                self.ok.show()
            else:
                self.eBar.showMessage('Ошибка изменения статуса задачи')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def bad_status_my_work(self):
        try:
            task_id = str(self.ui.lineTaskStatusId.text())
            is_changed = self.api.set_task_to_failed(self.user.account_address, task_id)
            if is_changed:
                self.ok.show()
            else:
                self.eBar.showMessage('Ошибка изменения статуса задачи')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def good_status_my_z(self):
        try:
            task_id = str(self.ui.lineTaskStatusIdZ.text())
            task_price = int(self.api.get_task_info(task_id)[3])
            is_changed = self.api.review_task(self.user.account_address, task_id, True, task_price)
            if is_changed:
                self.ok.show()
                self.ui.balanceLabel.setText((str(self.api.get_balance(self.user.account_address)) + " wei"))
            else:
                self.eBar.showMessage('Ошибка изменения статуса задачи')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

    def bad_status_my_z(self):
        try:
            task_id = str(self.ui.lineTaskStatusIdZ.text())
            #task_price = int(self.api.get_task_info(task_id)[3])
            is_changed = self.api.review_task(self.user.account_address, task_id, False, 0)
            if is_changed:
                self.ok.show()
            else:
                self.eBar.showMessage('Ошибка изменения статуса задачи')
        except Exception as e:
            self.eBar.showMessage(f'Ошибка: {e}')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    start = RegLog()
    start.show()

    sys.exit(app.exec_())
