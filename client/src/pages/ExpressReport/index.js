import React from 'react';

import './style.css'
import NewReportBase from './../NewReportBase'
import api from '../../services/api';
import ReconnectingWebSocket from 'reconnecting-websocket'
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import './../../config'
import {faSave, faRedo, faFileAlt} from "@fortawesome/free-solid-svg-icons";
import moment from 'moment';
import 'react-datetime/css/react-datetime.css';
import TimePicker from 'react-time-picker'
import DatePicker from 'react-date-picker'
import 'moment/locale/ru'
import {faCalendarAlt} from "@fortawesome/free-solid-svg-icons/faCalendarAlt";
import {faClock} from "@fortawesome/free-solid-svg-icons/faClock";
import Select from "react-select";

const reconnect_options = {
    //connectionTimeout: 600000,
    minReconnectionDelay: 10000,
    maxRetries: 1000
}

const selectStyles = {
    control: (base, state) => ({
        ...base,
        boxShadow: 'none',
        border: 'none'
    })
}

const actualDate = new Date()

class ExpressReport extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            callerPhone: '',
            callerCustomerType: '',
            callerContractRegion: '',
            cancelGround: '',
            baseCategory: '',
            subcategory: '',
            serviceCategory: '',
            serviceCode: '',
            enabledServiceCode: '',
            disabledServiceCode: '',
            mainIssueEffect: '',
            userEquipment: '',
            issueEmergeDate: actualDate,
            issueEmergeTime: actualDate,
            region: '',
            area: '',
            street: '',
            building: '',
            contactPerson: '',
            contactInfo: '',
            contactDate: actualDate,
            contactTime: actualDate,
            involvedEmployee: '',
            businessUnit: '',
            storeAddress: '',
            caseServiceCode: 100,
            refundingAmount: 0,
            extendedNotes: '',
            baseCategoryOptions: [],
            subcategoryOptions: [],
            serviceCategoryOptions: [],
            filteredBaseCategory: '',
            filteredSubcategories: [],
            customerTypeOptions: []
        };
        this.handleSubmit = this.handleSubmit.bind(this)
        this.refreshFormInputs = this.refreshFormInputs.bind(this)
    }

    componentDidMount() {
        api.get(`session/options/baseCategories?user_id=${localStorage.getItem('userId')}`, {
            headers: {
                'Authorization': localStorage.getItem('userToken')
            }
        }).then(response => {
            this.setState({
                baseCategoryOptions: response.data.map(option => (
                    { value: option.code,
                      label: '[' + option.code + ']  ' + option.name}
                ))
            })
        }).catch(err => {
            console.log(err)
        })

        api.get(`session/options/subcategories?user_id=${localStorage.getItem('userId')}`, {
            headers: {
                'Authorization': localStorage.getItem('userToken')
            }
        }).then(response => {
            this.setState({
                subcategoryOptions: response.data.map(option => (
                    { value: option.code,
                      label: '[' + option.code + ']  ' + option.name,
                      base: option.base_category_code_id
                    }
                )),
                filteredSubcategories: response.data.map(option => (
                    {   value: option.code,
                        label: '[' + option.code + ']  ' + option.name,
                        base: option.base_category_code_id}
                ))
            })
        }).catch(err => {
            console.log(err)
        })

        api.get(`session/options/serviceCategories?user_id=${localStorage.getItem('userId')}`, {
            headers: {
                'Authorization': localStorage.getItem('userToken')
            }
        }).then(response => {
            console.log('retrieval: ' + response)
            this.setState({
                serviceCategoryOptions: response.data.map(option => (
                    {
                        value: option.name,
                        label: option.name
                    }))
            })
        }).catch(err => {
            console.log(err)
        })

        this.setState({
            customerTypeOptions: [
                { value: 'None', label: 'Н/д' },
                { value: 'Individual', label: '[B2C] Физическое лицо' },
                { value: 'Corporate B2B', label: '[B2B] Корпоративный' },
                { value: 'Corporate B2G', label: '[B2G] Корпоративный' }
            ]
        })
    }

    hideNonPrimaryInputs = () => {



    }


    changeReportFillContext = (baseCategory) => {
        let subcategory = document.getElementById('subcategory-item')
        let serviceCategory = document.getElementById('service-category-item')
        let service = document.getElementById('service-select-item')
        let enabledService = document.getElementById('enabled-service-select-item')
        let disabledService = document.getElementById('disabled-service-select-item')
        let mainIssueEffect = document.getElementById('main-issue-effect-item')
        let equipment = document.getElementById('equipment-item')
        let issueStartTimestamp = document.getElementById('li-issue-start-timestamp')
        let issueOriginRegion = document.getElementById('issue-origin-region-item')
        let issueOriginArea = document.getElementById('issue-origin-area-item')
        let issueOriginStreet = document.getElementById('issue-origin-street-item')
        let issueOriginBuilding = document.getElementById('issue-origin-building-item')
        let contactPerson = document.getElementById('contact-person-item')
        let contactInfo = document.getElementById('contact-info-item')
        let contactTimePeriod = document.getElementById('li-contact-time-period')
        let involvedEmployee = document.getElementById('li-involved-employee')
        let businessUnit = document.getElementById('li-business-unit')
        let storeAddress = document.getElementById('store-address-item')
        let caseService = document.getElementById('li-case-service-select')
        let refundingAmount = document.getElementById('refunding-amount-item')
        let cancelGround = document.getElementById('cancel-ground-item')
        //let authFail = document.getElementById('auth-fail-item')


        subcategory.style.display = 'none'
        serviceCategory.style.display = 'none'
        service.style.display = 'none'
        enabledService.style.display = 'none'
        disabledService.style.display = 'none'
        mainIssueEffect.style.display = 'none'
        equipment.style.display = 'none'
        issueStartTimestamp.style.display = 'none'
        issueOriginRegion.style.display = 'none'
        issueOriginArea.style.display = 'none'
        issueOriginStreet.style.display = 'none'
        issueOriginBuilding.style.display = 'none'
        contactPerson.style.display = 'none'
        contactInfo.style.display = 'none'
        contactTimePeriod.style.display = 'none'
        involvedEmployee.style.display = 'none'
        businessUnit.style.display = 'none'
        storeAddress.style.display = 'none'
        caseService.style.display = 'none'
        refundingAmount.style.display = 'none'
        cancelGround.style.display = 'none'
        //authFail.style.display = 'none'

        switch (baseCategory) {
            case '100':
                //authFail.style.display = 'flex'
                cancelGround.style.display = 'flex'
                break;
            case '200':
                subcategory.style.display = 'flex'
                serviceCategory.style.display = 'flex'
                service.style.display = 'flex'
                break;
            case '300':
                subcategory.style.display = 'flex'
                serviceCategory.style.display = 'flex'
                service.style.display = 'flex'
                break
            case '400':
                subcategory.style.display = 'flex'
                serviceCategory.style.display = 'flex'
                enabledService.style.display = 'flex'
                disabledService.style.display = 'flex'
                break
            case '500':
                subcategory.style.display = 'flex'
                serviceCategory.style.display = 'flex'
                mainIssueEffect.style.display = 'flex'
                equipment.style.display = 'flex'
                issueStartTimestamp.style.display = 'flex'
                issueOriginRegion.style.display = 'flex'
                issueOriginArea.style.display = 'flex'
                issueOriginStreet.style.display = 'flex'
                issueOriginBuilding.style.display = 'flex'
                break
            case '600':
                serviceCategory.style.display = 'flex'
                service.style.display = 'flex'
                contactPerson.style.display = 'flex'
                contactInfo.style.display = 'flex'
                contactTimePeriod.style.display = 'flex'
                break
            case '700':
                subcategory.style.display = 'flex'
                serviceCategory.style.display = 'flex'
                caseService.style.display = 'flex'
                involvedEmployee.style.display = 'flex'
                businessUnit.style.display = 'flex'
                storeAddress.style.display = 'flex'
                refundingAmount.style.display = 'flex'
                break
            default:
                console.log('no visual changes unless base category gets different values or any evaluable assignment')
        }
    }

    handleSubmit = (event) => {
        const {name, value} = event.target;

        this.setState({
            [name]: value,
        })

        let issueStartTimestamp = ''

        if (isNaN(this.state.issueEmergeTime.valueOf())) {
            issueStartTimestamp = moment(this.state.issueEmergeDate).format('YYYY-MM-DD')
                + ' ' + this.state.issueEmergeTime
        } else {
            issueStartTimestamp = moment(this.state.issueEmergeDate).format('YYYY-MM-DD')
                + ' ' + moment(this.state.issueEmergeTime).format('HH:mm')
        }

        console.log('submitted timestamp 2: ' + issueStartTimestamp);
        console.log('submitted category ' + localStorage.getItem('baseCategory'));
        localStorage.setItem('baseCategory', '')
        localStorage.setItem('subcategory', '')
        //console.log('submitted contact timestamp: ' + this.state.contactTimePeriod);
    }

    refreshFormInputs = (inputElem, newPick) => {

        if (inputElem === 'issueEmergeDate') {
            this.setState({
                issueEmergeDate: newPick
            })
        } else if (inputElem === 'issueEmergeTime') {
            this.setState({
                issueEmergeTime: newPick
            })
        } else if (inputElem === 'contactDate') {
            this.setState({
                contactDate: newPick
            })
        } else if (inputElem === 'contactTime') {
            this.setState({
                contactTime: newPick
            })
        } else if (inputElem === 'baseCategory') {
            localStorage.setItem('baseCategory', newPick['value'])
            this.setState( {
                baseCategory: newPick,
                subcategory: '',
                filteredSubcategories: this.state.subcategoryOptions.filter(option => (
                    option['base'].toString() === localStorage.getItem('baseCategory')
                ))
            })

            this.changeReportFillContext(localStorage.getItem('baseCategory'))
            console.log('base category selected: ' + localStorage.getItem('baseCategory'))
        } else if (inputElem === 'subcategory') {
            localStorage.setItem('subcategory', newPick['value'])
            this.setState({
                subcategory: newPick,
                baseCategory: this.state.baseCategoryOptions.filter(cat => (
                    newPick['base'] === cat['value']
                )),
                renderTrigger: true
            })
            //let pickEnforced = this.state.baseCategoryOptions.filter(cat => (
              //  newPick['base'] === cat['value']
            //))
            //this.setState(this.state)
            //this.enforceBaseCatUpdate(pickEnforced)
            //this.refreshFormInputs('baseCategorySubEffect', baseCategoryPick)
            localStorage.setItem('baseCategory', this.state.baseCategory['value'])
            console.log('subcategory selected: ' + localStorage.getItem('subcategory'))
            console.log('base category selected: ' + localStorage.getItem('baseCategory'))
        } else if (inputElem === 'callerCustomerType') {
            this.setState({
                callerCustomerType: newPick
            })
        } else if (inputElem === 'serviceCategory') {
            this.setState({
                serviceCategory: newPick
            })
        }
    }

    enforceBaseCatUpdate(pickEnforced) {
        this.setState({
            baseCategory: this.state.baseCategoryOptions.filter(cat => (
                pickEnforced['base'] === cat['value']
            ))
        })
    }

    render() {

        const {
            baseCategory,
            subcategory,
            baseCategoryOptions,
            filteredSubcategories,
            callerCustomerType,
            customerTypeOptions,
            serviceCategory,
            serviceCategoryOptions
        } = this.state

        if (global.config.i18n.sockets.length === 0) {
            console.log('array length (ahead of websocket connection attempt): ', global.config.i18n.sockets.length)
            let ws = new ReconnectingWebSocket(localStorage.getItem('websocketAddress'), [], reconnect_options)
            global.config.i18n.sockets.push(ws)
            console.log('array length (evaluating connection attempt outcome): ', global.config.i18n.sockets.length)

            ws.onopen = () => {
                console.log('connection setup is complete')
            };

            ws.onmessage = (event) => {

                let transcriptPanel = document.getElementById('panel')
                let coreTranscriptPanel = document.getElementById('core-transcript-viewer')
                let completeTranscriptPanel = document.getElementById('complete-transcript-viewer')

                let feed = JSON.parse(event.data);
                let speaker = feed[0]['party']
                let text = feed[0]['text'];

                try {
                    if (text.includes('hangup')) {
                        //let feedValueUnmodified = feedValue.replace('(hangup)', '');
                        //completeTranscriptPanel.innerHTML = (coreTranscriptPanel.innerHTML + '<p>' + feedValueUnmodified + '</p>');
                        completeTranscriptPanel.innerHTML = coreTranscriptPanel.innerHTML
                        localStorage.setItem('fullTranscript', completeTranscriptPanel.innerHTML)
                        coreTranscriptPanel.innerHTML = '';
                        localStorage.setItem('partialTranscript', '')
                        localStorage.setItem('lastActiveSpeaker', '')
                        console.log('--- hangup completed ---');
                    } else {
                        if (localStorage.getItem('lastActiveSpeaker') === speaker)
                            coreTranscriptPanel.innerHTML = (localStorage.getItem('partialTranscript') + '<p>' + text + '</p>');
                        else {
                            coreTranscriptPanel.innerHTML = (localStorage.getItem('partialTranscript') + '<p><strong>' + speaker + ': </strong>' + text + '</p>');
                            localStorage.setItem('lastActiveSpeaker', speaker)
                        }
                        localStorage.setItem('partialTranscript', coreTranscriptPanel.innerHTML)
                        completeTranscriptPanel.innerHTML = '';
                        localStorage.setItem('fullTranscript', '')
                        transcriptPanel.scrollTop = transcriptPanel.scrollHeight + coreTranscriptPanel.scrollHeight
                        console.log('--- continuing call response ---')
                    }
                } catch (err) {
                    let refreshTranscript = localStorage.getItem('partialTranscript') + '<p><em>' + speaker + ': </em>' + text + '</p>'
                    localStorage.setItem('partialTranscript', refreshTranscript)
                }
            }

            ws.onclose = function (x) {
                console.log('connection is close');
                ws = null
            };
        }

        return (
            <NewReportBase>
                <div id="report-form-container">
                    <p id="compulsory-filling-note"><span style={{ color: "red", fontSize: "18px", fontWeight: 'bolder' }}>
                        *</span> - требует заполнения для регистрации отчёта
                    </p>
                    <form id="report-form">
                        <ul className="report-form-list">
                            <li>
                                <label htmlFor="caller-phone">Телефон</label>
                                <input id="caller-phone" type="tel" value="+71234567890" />
                            </li>

                            <li>
                                <label htmlFor="callerCustomerType">Тип клиента<span className="compulsory-field-label">*</span></label>
                                <Select className="form-select"
                                        components={{ DropdownIndicator:() => null, IndicatorSeparator: () => null }}
                                        id="calleCustomerType"
                                        name="callerCustomerType"
                                        value={callerCustomerType}
                                        options={customerTypeOptions}
                                        onChange={newPick => this.refreshFormInputs('callerCustomerType', newPick)}
                                        placeholder=""
                                        styles={selectStyles}
                                        autoFocus={false}
                                        isSearchable={true}
                                        required
                                />
                            </li>

                            <li>
                                <label htmlFor="caller-contract-region">Регион контракта</label>
                                <input id="caller-contract-region" type="text" />
                            </li>

                            <li>
                                <label htmlFor="base-category">Категория услуг КЦ<span className="compulsory-field-label">*</span></label>
                                <Select className="form-select"
                                    components={{ DropdownIndicator:() => null, IndicatorSeparator: () => null }}
                                    id="base-category"
                                    name="baseCategory"
                                    value={baseCategory}
                                    //value={this.state.baseCategory.value}
                                    options={baseCategoryOptions}
                                    onChange={newPick => this.refreshFormInputs('baseCategory', newPick)}
                                    placeholder=""
                                    styles={selectStyles}
                                    autoFocus={false}
                                    isSearchable={true}
                                    required
                                />
                            </li>

                            <li id="subcategory-item">
                                <label htmlFor="subcategory">Подкатегория услуг КЦ</label>
                                <Select className="form-select"
                                        components={{ DropdownIndicator:() => null, IndicatorSeparator: () => null }}
                                        id="subcategory"
                                        name="subcategory"
                                        value={subcategory}
                                        options={filteredSubcategories}
                                        onChange={newPick => this.refreshFormInputs('subcategory', newPick)}
                                        placeholder=""
                                        styles={selectStyles}
                                        autoFocus={false}
                                        isSearchable={true}
                                        required
                                />
                            </li>

                            {/* <li id="auth-fail-item">
                                <label htmlFor="caller-auth-failed">Результат обращения<span className="compulsory-field-label">*</span></label>
                                <input id="caller-auth-failed" type="text" required />
                            </li> */}

                            <li id="cancel-ground-item">
                                <label htmlFor="cancel-ground">Причина отказа в обслуживании<span className="compulsory-field-label">*</span></label>
                                <input id="cancel-ground" type="text" required />
                            </li>

                            <li id="service-category-item">
                                <label htmlFor="service-category">Вид услуг связи</label>
                                <Select className="form-select"
                                        components={{ DropdownIndicator:() => null, IndicatorSeparator: () => null }}
                                        id="serviceCategory"
                                        name="serviceCategory"
                                        value={serviceCategory}
                                        options={serviceCategoryOptions}
                                        onChange={newPick => this.refreshFormInputs('serviceCategory', newPick)}
                                        placeholder=""
                                        styles={selectStyles}
                                        autoFocus={false}
                                        isSearchable={true}
                                        required
                                />
                            </li>

                            <li id="service-select-item">
                                <label htmlFor="service-select">Услуга / продукт<span className="compulsory-field-label">*</span></label>
                                <input id="service-select" type="text" />
                            </li>

                            <li id="enabled-service-select-item">
                                <label htmlFor="enabled-service-select">Подключенная / заказанная услуга</label>
                                <input id="enabled-service-select" type="text" />
                            </li>

                            <li id="disabled-service-select-item">
                                <label htmlFor="disabled-service-select">Отключенная услуга</label>
                                <input id="disabled-service-select" type="text" />
                            </li>

                            <li id="main-issue-effect-item">
                                <label htmlFor="main-issue-effect">Основной признак неполадок<span className="compulsory-field-label">*</span></label>
                                <input id="main-issue-effect" type="text" required />
                            </li>

                            <li id="equipment-item">
                                <label htmlFor="equipment">Используемое оборудование<span className="compulsory-field-label">*</span></label>
                                <input id="equipment" type="text" required />
                            </li>

                            <li id="li-issue-start-timestamp">
                                <label htmlFor="issue-start-timestamp">Дата / время возникновения неполадок<span className="compulsory-field-label">*</span></label>
                                <div id="issue-start-timestamp">
                                    <DatePicker
                                        name="issueEmergeDate"
                                        value={this.state.issueEmergeDate}
                                        locale="ru"
                                        format="dd.MM.y"
                                        clearIcon={null}
                                        isOpen={false}
                                        calendarIcon={null}
                                        onChange={newPick => this.refreshFormInputs('issueEmergeDate', newPick)}
                                    />
                                    <FontAwesomeIcon icon={faCalendarAlt} />
                                    <TimePicker
                                        name="issueEmergeTime"
                                        value={this.state.issueEmergeTime}
                                        clearIcon={null}
                                        isOpen={false}
                                        disableClock={true}
                                        onChange={newPick => this.refreshFormInputs('issueEmergeTime', newPick)}
                                    />
                                    <FontAwesomeIcon icon={faClock} />
                                </div>
                            </li>
                            <li id="issue-origin-region-item">
                                <label htmlFor="issue-origin-region">Регион пользования услугами</label>
                                <input id="issue-origin-region" type="text" />
                            </li>

                            <li id="issue-origin-area-item">
                                <label htmlFor="issue-origin-area">Город / населённый пункт<span className="compulsory-field-label">*</span></label>
                                <input id="issue-origin-area" type="text" required />
                            </li>

                            <li id="issue-origin-street-item">
                                <label htmlFor="issue-origin-street">Улица</label>
                                <input id="issue-origin-street" type="text"/>
                            </li>

                            <li id="issue-origin-building-item">
                                <label htmlFor="issue-origin-building">Дом / строение / корпус</label>
                                <input id="issue-origin-building" type="text"/>
                            </li>

                            <li id="contact-person-item">
                                <label htmlFor="contact-person">Контактное лицо<span className="compulsory-field-label">*</span></label>
                                <input id="contact-person" type="text" required />
                            </li>

                            <li id="contact-info-item">
                                <label htmlFor="contact-info">Контактная информация<span className="compulsory-field-label">*</span></label>
                                <input id="contact-info" type="text" required />
                            </li>

                            <li id="li-contact-time-period">
                                <label htmlFor="contact-time-period">Предпочтительные дата / время обращения<span className="compulsory-field-label">*</span></label>
                                <div id="contact-time-period">
                                    <DatePicker
                                        name="contactDate"
                                        value={this.state.contactDate}
                                        locale="ru"
                                        format="dd.MM.y"
                                        clearIcon={null}
                                        isOpen={false}
                                        calendarIcon={null}
                                        onChange={newPick => this.refreshFormInputs('contactDate', newPick)}
                                    />
                                    <FontAwesomeIcon icon={faCalendarAlt} />
                                    <TimePicker
                                        name="contactTime"
                                        value={this.state.contactTime}
                                        clearIcon={null}
                                        isOpen={false}
                                        disableClock={true}
                                        onChange={newPick => this.refreshFormInputs('contactTime', newPick)}
                                    />
                                    <FontAwesomeIcon icon={faClock} />
                                </div>
                            </li>

                            <li id="li-involved-employee">
                                <label htmlFor="involved-employee">Идентификационные данные сотрудника</label>
                                <input id="involved-employee" type="text" />
                            </li>

                            <li id="li-business-unit">
                                <label htmlFor="business-unit">Ответственное подразделение / представительство оператора</label>
                                <input id="business-unit" type="text" />
                            </li>
                            <li id="store-address-item">
                                <label htmlFor="store-address">Адрес пункта обслуживания</label>
                                <input id="store-address" type="text" />
                            </li>

                            <li id="li-case-service-select">
                                <label htmlFor="case-service-select">Причина компенсации (услуга / продукт)</label>
                                <input id="case-service-select" type="text" />
                            </li>

                            <li id="refunding-amount-item">
                                <label htmlFor="refunding-amount">Сумма компенсации</label>
                                <input id="refunding-amount" type="text" />
                            </li>

                            <li>
                                <label id="extended-notes" htmlFor="extended-notes">Детали обращения</label>
                                <textarea id="extended-notes" />
                            </li>
                        </ul>
                        <div id="report-form-btns">
                            <button id="reset-btn" type="reset" ><FontAwesomeIcon icon={faRedo} style={{ marginRight: "5px" }} />Сброс</button>
                            <button id="save-btn" type="submit" onClick={this.handleSubmit}><FontAwesomeIcon icon={faFileAlt} style={{ marginRight: "5px" }} />Регистрация</button>
                        </div>
                    </form>
                </div>
            </NewReportBase>
        )
    }
}

export default ExpressReport;