'use strict';
// Все строго! Никаких var!

// Перевод разделителей \н в <бр>  
function _newline(text) {
  return text.split('\n').map((item, idx) => {
    return (idx === 0) ? item : [<br key={idx} />, item]
  });
}

// загрузчик данных json по задачам 1 и 2
function loadSpending(url){
  // цепочка промисов, по окончании которой отрендерится таблица
  fetch(url)
  .then(response => response.json())
  .then(result => {
    // console.log(result.data);
    ReactDOM.render(
      <MainTable data={result.data}/>,
      document.getElementById('react_body')
    );
  });
}

// обработчики нажатий на сслыку для прорисовки таблиц из задач 1 и 2
function handleSpending(e){
  // отмена действия для ссылки по-умолчанию
  e.preventDefault();
  loadSpending('/api/spending');
}

function handleSpendingByMnn(e){
  e.preventDefault();
  loadSpending('/api/spending_by_mnn');
}

// отдельный с обработчик с загрузкой для таблицы из задачи 3
function handleMedicine(e){
  e.preventDefault();
  fetch('/api/medicine')
  .then(response => response.json())
  .then(result => {
    console.log(result.data);
    ReactDOM.render(
      <AltTable data={result.data}/>,
      document.getElementById('react_body')
    );
  });
}

// Проприсовка меню. Для обработки активного состояния придется переходить к классовому представлению с состояниями...
function NavMenu(){
  return (
      <ul className="nav nav-tabs">
        <li className="nav-item"><a className="nav-link" href="#" onClick={handleSpending}>Затраты</a></li>
        <li className="nav-item"><a className="nav-link" href="#" onClick={handleSpendingByMnn}>Затраты по МНН</a></li>
        <li className="nav-item"><a className="nav-link" href="#" onClick={handleMedicine}>Лекарственные средства</a></li>
      </ul>
    );
}

// Модель одной строки в таблице 1 и 2
function MainTableItem(props){
  // Наименование полей действительно лучше сократить.
  const data = props.data,
        mnn = data["Международное непатентованное наименование"],
        tn = data["Торговое наименование"],
        tn_split = _newline(tn),
        form = data["Форма выпуска"],
        form_split = _newline(form),
        qty = +data["Количество"],
        price = +data["Цена"],
        summary = qty * price;
  return (
    <tr>
      <td>{mnn}</td>
      <td>{tn_split}</td>
      <td>{form_split}</td>
      <td>{qty}</td>
      <td>{price.toFixed(2)}</td>
      <td>{summary.toFixed(2)}</td>
    </tr> 
  );
}

// Модель таблицы для задач 1 и 2
function MainTable(props){
  const data = props.data;
  const rows = data.map((row) =>
    <MainTableItem data={row} key={row.key}/>
  ); // Ключи - элемент, без которого вся консоль засыпана предупреждениями

  // Были попытки посчитать все на стадии рендеринга... 
  // Как больно осозновать что вызывающая функция завершилась раньше вложенной и в результирующую строку пришли нули.
  // Проще всего пробежаться по списку лишний раз для подсчета значений. Можно через reduce, но так надежнее
  let qty = 0, price = 0, summary = 0;
  data.forEach((row) => {
    let q = +row['Количество'],
        p = +row['Цена'];
    qty += q;
    price += p;
    summary += (q * p);
  });

  
  return (
    <table className="table table-bordered table-hover">
        <thead>
        <tr className="bg-warning">
            <th scope="col">Международное непатентованное наименование</th>
            <th scope="col">Торговое наименование</th>
            <th scope="col">Форма выпуска</th>
            <th scope="col">Количество</th>
            <th scope="col">Цена</th>
            <th scope="col">Затраты</th>
        </tr>
        </thead>
        <tbody>  
            {rows}
          <tr>
            <td colSpan="3"></td>
            <td className='border-2 border-warning fw-bold'>{qty}</td>
            <td className='border-2 border-warning fw-bold'>{price.toFixed(2)}</td> 
            <td className='border-2 border-warning fw-bold'>{summary.toFixed(2)}</td>
          </tr> 
        </tbody>
    </table>
  );
}
// price.toFixed(2) - забавно что Math.round() округляет только до целого 

// Модель строки таблицы 3
function AltTableItem(props){
  const data = props.data,
        idx = props.idx,
        mnn = data["mnn"],
        tn = data["tn"],
        ven = data["ven"],
        tn_split = _newline(tn);
  return (
    <tr>
        <td>{idx+1}</td>
        <td>{mnn}</td>
        <td>{tn_split}</td>
        <td className="text-center">{ ven ? 'V':'N' }</td>
    </tr>
  );
}

// Модель таблицы для задачи 3
function AltTable(props){
  const ven = props.data.ven;
  const group1 = ven.map((row, idx) =>
    <AltTableItem data={row} idx={idx} key={row.key}/>
  );

  const other = props.data.other;
  const group2 = other.map((row, idx) =>
    <AltTableItem data={row} idx={idx} key={row.key}/>
  );

  return (
    <table className="table table-bordered table-hover">
    <thead>
    <tr className="bg-warning">
        <th className="text-center" scope="col">№</th>
        <th className="text-center" scope="col">МНН</th>
        <th className="text-center" scope="col">ТН</th>
        <th className="text-center" scope="col">ЖНВЛП</th>
    </tr>
    </thead>
    <tbody>
    <tr><td className="bg-secondary text-white text-center" colSpan="4">ЛС в перечне ЖНВЛП</td></tr>
      {group1}
    <tr><td className="bg-secondary text-white text-center" colSpan="4">Остальные ЛС</td></tr>
      {group2}
    </tbody>
</table>
  );
}

// Инициируем меню
ReactDOM.render(
  <NavMenu />,
  document.getElementById('react_head')
);
