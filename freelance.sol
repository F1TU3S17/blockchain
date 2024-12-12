// SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.0;

contract Freelance {
    struct Task {
        uint256 id; //id задачи
        address customer; //Заказчик
        address executor; //Исполниетель задачи
        uint256 price; //Стоимость исполнения задачи
        Status status; //Статус задачи
        string title; //Название задачи
        string discripcion; //Описание задачи
    }

    enum Status {
        inSearch, //В поиске
        inWork, //В работе
        done, //Выполнена
        completed, //Завершена
        failed //Провалена
    }

    address public admin;
    uint256 currentId = 0; //id задания, которое будет добавлено следующим
    uint256[] public tasks; //массив id задач
    mapping(address => uint256[]) public usersTasks; //маппинг ключ - адресс пользователя, значение - массив с id задачами пользователя
    mapping(uint256 => Task) public tasksMap; //общий маппинг задач

    constructor() {
        admin = msg.sender;
    }

    modifier onlyExecutor(uint256 id, address executor) {
        require(tasksMap[id].customer != executor, "It`s your task!!!");
        _;
    }

    modifier onlyCustomer(uint256 id, address customer) {
        require(tasksMap[id].executor != customer, "It`s not your task!!!");
        _;
    }

    //Функция добавления задачи на биржу
    function addTask(
        address customer,
        uint256 price,
        string memory title,
        string memory discripcion
    ) public {
        require(tasksMap[currentId].id == uint256(0), "Id zanat");
        Task memory newTask = Task(
            currentId,
            customer,
            address(0),
            price,
            Status.inSearch,
            title,
            discripcion
        );
        tasks.push(currentId);
        tasksMap[currentId] = newTask;
        usersTasks[customer].push(currentId);
        currentId += 1;
    }

    // Функция для добавления задачи Исполнителю
    function setTaskToWork(address executor, uint256 taskId)
        public
        onlyExecutor(taskId, executor)
    {
        require(tasks.length != 0, "Empty array!!!");
        require(
            tasksMap[taskId].status == Status.inSearch,
            "This task complicte or in work"
        );
        tasksMap[taskId].executor = executor;
        tasksMap[taskId].status = Status.inWork;
        usersTasks[executor].push(taskId);
    }

    function setTaskToDone(address executor, uint256 taskId)
        public
        onlyExecutor(taskId, executor)
    {
        require(
            tasksMap[taskId].status == Status.inWork,
            "task not in work!!!"
        );
        require(tasks.length != 0, "Empty array!!!");
        tasksMap[taskId].status = Status.done;
    }

    function setTaskToFailed(address executor, uint256 taskId)
        public
        onlyExecutor(taskId, executor)
    {
        require(
            tasksMap[taskId].status == Status.inWork,
            "task not in work!!!"
        );
        require(tasks.length != 0, "Empty array!!!");
        tasksMap[taskId].status = Status.failed;
    }

    function reviewTask(
        address customer,
        uint256 taskId,
        bool isDone
    ) public payable onlyCustomer(taskId, customer) {
        require(tasks.length != 0, "Empty array!!!");
        require(tasksMap[taskId].status == Status.done, "task don`t done!!!");
        if (isDone) {
            tasksMap[taskId].status = Status.completed;
            require(msg.value >= tasksMap[taskId].price, "Wrong money!!!");
            payable(tasksMap[taskId].executor).transfer(tasksMap[taskId].price);
        } else {
            tasksMap[taskId].status = Status.failed;
        }
    }

    function getAllTasksId() public view returns (uint256[] memory) {
        return tasks;
    }

    function getUsersTasks(address userAddress)
        public
        view
        returns (uint256[] memory)
    {
        return usersTasks[userAddress];
    }
}
