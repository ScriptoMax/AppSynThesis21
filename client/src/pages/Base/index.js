import React from 'react';
import {useHistory} from 'react-router-dom';

import './style.css';
import Header from '../Components/Header'
import {Button} from "react-bootstrap";
import api from "../../services/api";
import ControlAction from "../ControlAction";

export default function Dashboard({children}) {

    const action = new ControlAction()

    const history = useHistory();

    async function setControlElement() {

        let switchBtn = document.getElementById('btn-session-control');
        let liveReportBtn = document.getElementById('btn-live-report');

        if (switchBtn.innerHTML === "Создать отчёт") {
            switchBtn.style.backgroundColor = "#DA5237";
            switchBtn.innerHTML = "Завершить";
            liveReportBtn.style.display = 'block';
            switchBtn.onmouseover = function () {
                this.style.backgroundColor = "#F7451E";
            }
            switchBtn.onmouseleave = function () {
                this.style.backgroundColor = "#DA5237";
            }
            //await action.handleInitRequest().then(r => console.log('session opening is complete'))
        } else {
            switchBtn.style.backgroundColor = "#4FA93A";
            switchBtn.innerHTML = "Создать отчёт";
            liveReportBtn.style.display = 'none';
            switchBtn.onmouseover = function () {
                this.style.backgroundColor = "#5EC033";
            }
            switchBtn.onmouseleave = function () {
                this.style.backgroundColor = "#4FA93A";
            }
            //await action.handleCancelRequest().then(r => console.log('session closing is complete'))
        }
    }

    function linkToReport() {
        history.push('/expressReport')
    }

    return(
        <div className="full-page">
            <Header/>
            <div className="container-dashboard">
                <section className="menu-sidebar">
                    <div className="menu-body">
                        {localStorage.getItem('sessionStatus') === 'close' ? (
                            <Button id="btn-session-control" onClick={setControlElement}>Создать отчёт</Button>
                            ) : (
                            <Button id="btn-session-control" onClick={setControlElement} style={{ backgroundColor: '#F7451E' } }>Завершить</Button>
                            )
                        }

                        {localStorage.getItem('sessionStatus') === 'active' ? (
                            <Button id="btn-live-report" onClick={linkToReport}>
                                Текущий отчёт
                            </Button>
                            ) : (
                            <Button id="btn-live-report" onClick={linkToReport}  style={{ display: "none" }}>
                                Текущий отчёт
                            </Button>
                            )
                        }
                    </div>
                </section>
                <section className="content-dashboard">
                    {children}
                </section>
            </div>
            {/* <Footer/> */}
        </div>
    );
}