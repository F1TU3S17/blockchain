import web3
import json
import os
class API():
    # От ганача: http://127.0.0.1:7545
    w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
    contract_address = web3.Web3.to_checksum_address('0xA0fFE3532e5727fdDA011803caB224f9FB21126A')
    with open('abi.txt','r') as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=contract_address, abi=abi)

    def accounts(self):
        accounts = self.w3.eth.accounts
        return accounts


    def get_balance(self, account):
        account_address = web3.Web3.to_checksum_address(account)
        balance = self.w3.eth.get_balance(account_address)
        return balance


    def get_admin(self):
        admin_address = self.contract.functions.admin().call()
        return admin_address

    def get_tasks_id_list(self):
        task_list = self.contract.functions.getAllTasksId().call()
        return task_list

    def get_task_info(self, task_id):
        try:
            task_info = self.contract.functions.tasksMap(int(task_id)).call()
            return task_info
        except Exception as e:
            print(f'Ошибка {e}')

    def get_all_tasks_in_search(self):
        tasks_id_list = self.get_tasks_id_list()
        tasks_len = len(tasks_id_list)
        tasks = []
        for i in range(0, tasks_len):
            task = self.get_task_info(tasks_id_list[i])
            if int(task[4]) == 0:
                tasks.append(task)

        tasks = self.transform_all_info_to_ui(tasks)
        return tasks

    def get_user_task(self, user_address):
        user_address = web3.Web3.to_checksum_address(user_address)
        tasks = self.contract.functions.getUsersTasks(user_address).call()
        return tasks

    def add_task(self, customer_address, price, title, description):
        try:
            value = 0
            customer_address = web3.Web3.to_checksum_address(customer_address)
            price = int(price)
            title = str(title)
            description = str(description)
            self.contract.functions.addTask(customer_address, price, title, description).transact({'from': customer_address, 'value': value})
            return True
        except Exception as e:
            print(f'Ошибка {e}')
        return False

    def task_to_work(self, executor_address, task_id):
        try:
            executor_address = web3.Web3.to_checksum_address(executor_address)
            task_id = int(task_id)
            self.contract.functions.setTaskToWork(executor_address, task_id).transact({'from': executor_address, 'value': 0})
            return True
        except Exception as e:
            print(f'Ошибка {e}')
        return False

    def set_task_to_done(self, executor_address, task_id):
        try:
            executor_address = web3.Web3.to_checksum_address(executor_address)
            task_id = int(task_id)
            self.contract.functions.setTaskToDone(executor_address, task_id).transact({'from': executor_address, 'value': 0})
            return True
        except Exception as e:
            print(f'Ошибка {e}')
        return False

    def set_task_to_failed(self, executor_address, task_id):
        try:
            executor_address = web3.Web3.to_checksum_address(executor_address)
            task_id = int(task_id)
            self.contract.functions.setTaskToFailed(executor_address, task_id).transact({'from': executor_address, 'value': 0})
            return True
        except Exception as e:
            print(f'Ошибка {e}')
        return False

    def review_task(self, customer_address, task_id, task_bool_status, task_price):
        try:
            customer_address = web3.Web3.to_checksum_address(customer_address)
            task_id = int(task_id)
            task_bool_status = bool(task_bool_status)
            task_price = int(task_price)
            self.contract.functions.reviewTask(customer_address, task_id, task_bool_status).transact({"from": customer_address, 'value': task_price})
            return True
        except Exception as e:
            print(f'Ошибка {e}')
        return False

    def customer_history(self, account_address):
        account_address = str(web3.Web3.to_checksum_address(account_address))
        history = self.get_user_task(account_address)
        customer_history = []
        for task_id in history:
            if str(self.get_task_info(task_id)[1]) == account_address:
                customer_history.append(self.get_task_info(task_id))
        return customer_history

    def executor_history(self, account_address):
        account_address = str(web3.Web3.to_checksum_address(account_address))
        history = self.get_user_task(account_address)
        executor_history = []
        for task_id in history:
            if str(self.get_task_info(task_id)[2]) == account_address:
                executor_history.append(self.get_task_info(task_id))
        return executor_history

    def task_to_execute(self, account_address):
        account_address = str(web3.Web3.to_checksum_address(account_address))
        tasks = self.get_user_task(account_address)
        tasks_to_execute = []
        for task_id in tasks:
            if str(self.get_task_info(task_id)[2]) == account_address and (str(self.get_task_info(task_id)[4]) == '1'):
                tasks_to_execute.append(self.get_task_info(task_id))

        return tasks_to_execute

    def customer_tasks(self, account_address):
        account_address = str(web3.Web3.to_checksum_address(account_address))
        tasks = self.get_user_task(account_address)
        customer_tasks = []
        for task_id in tasks:
            if str(self.get_task_info(task_id)[1]) == account_address and (str(self.get_task_info(task_id)[4]) == '2'):
                customer_tasks.append(self.get_task_info(task_id))
        return customer_tasks
    def registration(self, nickname, login, password):
        path = 'data.txt'
        is_exist = os.path.exists(path)
        if is_exist:
            with open('data.txt', 'r') as f:
                data = json.load(f)
                users_data = data["users"]
                user = [l for l in users_data.keys() if login == l]
                if user:
                    return False
                data['users'][str(login)] = {
                    "nickname": nickname,
                    "password": password
                }
                with open('data.txt','w') as nf:
                    json.dump(data,nf)
                    nf.close()
                    f.close()
                    return True
        else:
            data = {}
            data['users'] = {}
            data['users'][str(login)]={
                "nickname": nickname,
                "password": password
            }
            with open('data.txt','w') as f:
                json.dump(data, f)
            f.close()
            return True

    def login(self, login, password):
        with open('data.txt', 'r') as f:
            try:
                login = str(login)
                password = str(password)
                data = json.load(f)
                user_data = data['users']
                logins = user_data.keys()
                control_sum = 0
                if login in logins and user_data[login]['password'] == password:
                    f.close()
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Erorr!!! {e}")
            return False

    def get_user_nickname(self, login):
        try:
            with open('data.txt','r') as f:
                data = json.load(f)
                users_data = data["users"]
                nickname = users_data[login]['nickname']
                f.close()
                return nickname
        except Exception as e:
            print(f'Error: {e}!!!')

    def get_status(self, status):
        str_status = 'Неизвестный статус'
        try:
            status = int(status)
            if status == 0:
                str_status = 'В поиске'
            elif status == 1:
                str_status = 'В работе'
            elif status == 2:
                str_status = 'Выполнена, на утверждении'
            elif status == 3:
                str_status = 'Выполнена, оплачена'
            elif status == 4:
                str_status = 'Провалена'
        except Exception as e:
            print(f'Error: {e}!!!')
        return str_status

    def transform_all_info_to_ui(self, tasks_list):
        len_task_list = len(tasks_list)
        len_task = 7 #кол-во элементов, описывающих в задачу
        for i in range(len_task_list):
            for j in range(len_task):
                if j == 2 and str(tasks_list[i][j]) == '0x0000000000000000000000000000000000000000':
                    tasks_list[i][j] = 'В поиске'
                if j == 4:
                    tasks_list[i][j] = self.get_status(tasks_list[i][j])
                if j == 3:
                    tasks_list[i][j] = str(tasks_list[i][j]) + " wei"
        return tasks_list

#api = API()
#print(api.get_all_tasks_in_search())
#print(api.customer_history(0xB9181d0422b6DFD48DC5362e99118B7a9F519D32))
#print(api.executor_history(0xB9181d0422b6DFD48DC5362e99118B7a9F519D32))
#print(api.registration("nikHay", "0xB9181d0422b6DFD48DC5362e99118B7a9F519D32","123"))
#print(api.get_user_nickname('0xB9181d0422b6DFD48DC5362e99118B7a9F519D32'))
#print(api.add_task('0xB9181d0422b6DFD48DC5362e99118B7a9F519D32', 1005, 'Сделайте сайт','Интернет-магазин'))
#print(api.task_to_work('0x373C4474C1C183745193c14c1507B7BA490231FA',1))
#print(api.set_task_to_done('0x373C4474C1C183745193c14c1507B7BA490231FA', 1))
#print(api.review_task('0xB9181d0422b6DFD48DC5362e99118B7a9F519D32', 1, True, 1000))