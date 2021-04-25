import React from 'react';

import {Table, Button} from 'react-bootstrap';
import api from '../../services/api';
import Base from './../Base'
import Modal from "./modal";
import './style.css';

class Dashboard extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            reports: [],
            reportDetails: {},
            isModalVisible: false
        }
        this.openModal = this.openModal.bind(this)
        this.closeModal = this.closeModal.bind(this)
    }

    componentDidMount() {
        api.get(`session/${localStorage.getItem('userId')}/reports`, {
            headers: {
                'Authorization': localStorage.getItem('userToken')
            }
        }).then(response => {
            this.setState({
                reports: response.data
            })
        }).catch(err => {
            console.log(err)
        })
    }

    openModal(event) {

        let report_id = event.target.getAttribute('id')

        api.get(`session/report/${report_id}?user_id=${localStorage.getItem('userId')}`, {
            headers: {
                'Authorization': localStorage.getItem('userToken')
            }
        }).then(response => {
            this.setState({
                reportDetails: response.data
            })
        }).catch(err => {
            console.log(err)
        })

        this.setState({
            isModalVisible: true
        })
    }

    closeModal() {
        this.setState({
            isModalVisible: false
        })
    }

    render() {

        const {
            reports
        } = this.state

        const {
            reportDetails
        } = this.state

        return (

            <Base>
                <div className="container container-list-reports">
                    <p id="report-list-title"
                       style={{fontSize: '20px', textAlign: "left", marginBottom: '5px'}}>Отчёты
                        о принятых звонках (последние 10)</p>
                    <Table striped bordered hover>
                        <thead>
                        <tr>
                            <th style={{width: '5%'}}>№</th>
                            <th style={{width: '10%'}}>Телефон</th>
                            <th style={{width: '15%'}}>Регион контракта</th>
                            <th style={{width: '20%'}}>Категория услуг КЦ</th>
                            <th style={{width: '30%'}}>Подкатегория услуг КЦ</th>
                            <th style={{width: '20%'}}>Дата / время регистрации</th>
                        </tr>
                        </thead>
                        <tbody>
                        {
                            reports.map(report => (
                                    <tr key={report.report_id}>
                                        <td>{report.report_id}</td>
                                        <td>{report.caller_phone}</td>
                                        { report.caller_contract_region !== undefined && report.caller_contract_region !== null && report.caller_contract_region.length > 0 ? (
                                        <td>{report.caller_contract_region}</td>
                                            ) : (<td>Н/д</td>)}
                                        <td>[{report.base_category_code_id}] {report.base_category}</td>
                                        { report.subcategory_code_id !== undefined && report.subcategory_code_id !== null ? (
                                                <td>[{report.subcategory_code_id}] {report.subcategory}</td>
                                        ) : (<td>Н/д</td>)}
                                        <td>{report.registered_on}</td>
                                        <td>
                                                <a
                                                    id={report.report_id}
                                                    onClick={this.openModal}
                                                    style={{ color: "#123952", fontWeight: "bolder", textDecoration: "underline", cursor: "pointer"}}>
                                                    >>
                                                </a>
                                            <Modal id="popup-details" isOpen={this.state.isModalVisible} onClose={() => this.closeModal()}>
                                                <div className="modal-table-container">
                                                    <p id="report-caption">№ {reportDetails.report_id}</p>
                                                    <Table striped bordered hover id="modal-table-base">
                                                        <tr>
                                                            <td>Дата / время регистрации</td>
                                                            <td>{reportDetails.registered_on}</td>
                                                        </tr>
                                                        <tr>
                                                            <td>Телефон</td>
                                                            <td>{reportDetails.caller_phone}</td>
                                                        </tr>
                                                        <tr>
                                                            <td>Тип клиента</td>
                                                            <td>{reportDetails.caller_customer_type}</td>
                                                        </tr>

                                                        { reportDetails.caller_contract_region !== undefined && reportDetails.caller_contract_region !== null && reportDetails.caller_contract_region.length > 0 ? (
                                                        <tr>
                                                            <td>Регион контракта</td>
                                                            <td>{reportDetails.caller_contract_region}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        <tr>
                                                            {reportDetails.base_category_code_id === 100 ? (
                                                                <td>Результат обращения</td>
                                                            ) : (
                                                                <td>Категория оказанных услуг</td>
                                                            )
                                                            }
                                                            <td>[{reportDetails.base_category_code_id}]&nbsp;&nbsp;{reportDetails.base_category}</td>
                                                        </tr>
                                                        <tr>
                                                            {reportDetails.base_category_code_id === 100 ? (
                                                                    <td>Причина отказа в обслуживании</td>
                                                                ) : (
                                                                    <td>Подкатегория услуг</td>
                                                                )
                                                            }
                                                            <td>[{reportDetails.subcategory_code_id}]&nbsp;&nbsp;{reportDetails.subcategory}</td>
                                                        </tr>

                                                        { (reportDetails.service_category !== undefined && reportDetails.service_category !== null) ? (
                                                            <tr>
                                                                <td>Сегмент услуг связи</td>
                                                                <td>{reportDetails.service_category}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.service_code_id !== undefined && reportDetails.service_code_id !== null ? (
                                                        <tr>
                                                            <td>Услуга / продукт</td>
                                                            <td>[{reportDetails.service_code_id}]&nbsp;&nbsp;{reportDetails.service_name}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.enabled_service_code_id !== undefined && reportDetails.enabled_service_code_id !== null ? (
                                                        <tr>
                                                            <td>Подключенная / заказанная услуга</td>
                                                            <td>[{reportDetails.enabled_service_code_id}]&nbsp;&nbsp;{reportDetails.enabled_service_category}&nbsp;&nbsp;&nbsp;>&nbsp;&nbsp;&nbsp;{reportDetails.enabled_service_name}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.disabled_service_code_id !== undefined && reportDetails.disabled_service_code_id !== null ? (
                                                            <tr>
                                                                <td>Отключенная услуга</td>
                                                                <td>[{reportDetails.disabled_service_code_id}]&nbsp;&nbsp;{reportDetails.disabled_service_category}&nbsp;&nbsp;&nbsp;>&nbsp;&nbsp;&nbsp;{reportDetails.disabled_service_name}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.main_issue_effect !== undefined && reportDetails.main_issue_effect !== null ? (
                                                        <tr>
                                                            <td>Основной признак неполадок</td>
                                                            <td>{reportDetails.main_issue_effect}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.user_equipment !== undefined && reportDetails.user_equipment !== null ? (
                                                        <tr>
                                                            <td>Используемое оборудование</td>
                                                            <td>{reportDetails.user_equipment}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.start_timestamp !== undefined && reportDetails.start_timestamp !== null ? (
                                                        <tr>
                                                            <td>Дата / время возникновения неполадок</td>
                                                            <td>{reportDetails.start_timestamp}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.region !== undefined && reportDetails.region !== null  && reportDetails.region.length > 0 ? (
                                                        <tr>
                                                            <td>Регион пользования услугами</td>
                                                            <td>{reportDetails.region}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.area !== undefined && reportDetails.area !== null ? (
                                                        <tr>
                                                            <td>Город / населённый пункт</td>
                                                            <td>{reportDetails.area}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.street !== undefined && reportDetails.street !== null  && reportDetails.street.length > 0 ? (
                                                        <tr>
                                                            <td>Улица</td>
                                                            <td>{reportDetails.street}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.building !== undefined && reportDetails.building !== null  && reportDetails.building.length > 0 ? (
                                                        <tr>
                                                            <td>Дом / строение / корпус</td>
                                                            <td>{reportDetails.building}</td>
                                                        </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.contact_person !== undefined && reportDetails.contact_person !== null ? (
                                                            <tr>
                                                                <td>Контактное лицо</td>
                                                                <td>{reportDetails.contact_person}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.contact_info !== undefined && reportDetails.contact_info !== null ? (
                                                            <tr>
                                                                <td>Контактная информация</td>
                                                                <td>{reportDetails.contact_info}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.contact_time_period !== undefined && reportDetails.contact_time_period !== null ? (
                                                            <tr>
                                                                <td>Предпочтительные дата / время обращения</td>
                                                                <td>{reportDetails.contact_time_period}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.involved_employee !== undefined && reportDetails.involved_employee !== null  && reportDetails.involved_employee.length > 0 ? (
                                                            <tr>
                                                                <td>Идентификационные данные сотрудника</td>
                                                                <td>{reportDetails.involved_employee}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.business_unit !== undefined && reportDetails.business_unit !== null  && reportDetails.business_unit.length > 0 ? (
                                                            <tr>
                                                                <td>Ответственное подразделение / представительство оператора</td>
                                                                <td>{reportDetails.business_unit}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.store_address !== undefined && reportDetails.store_address !== null  && reportDetails.store_address.length > 0 ? (
                                                            <tr>
                                                                <td>Адрес пункта обслуживания</td>
                                                                <td>{reportDetails.store_address}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.case_service_code_id !== undefined && reportDetails.case_service_code_id !== null ? (
                                                            <tr>
                                                                <td>Причина компенсации (услуга / продукт)</td>
                                                                <td>[{reportDetails.case_service_code_id}]&nbsp;&nbsp;{reportDetails.case_service_category}&nbsp;&nbsp;&nbsp;>&nbsp;&nbsp;&nbsp;{reportDetails.case_service_name}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}

                                                        { reportDetails.refunding_amount !== undefined ? (
                                                            <tr>
                                                                <td>Сумма к возврату</td>
                                                                <td>{reportDetails.refunding_amount}</td>
                                                            </tr>
                                                        ) : (<tr style={{ display: "none" }} />)}
                                                    </Table>
                                                </div>
                                                <Button id="btn-close-modal" onClick={this.closeModal}>Закрыть</Button>
                                            </Modal>
                                        </td>
                                    </tr>
                                )
                            )
                        }
                        </tbody>
                    </Table>
                </div>
            </Base>

        );
    }
}

export default Dashboard;