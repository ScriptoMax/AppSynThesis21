import Header from "../Components/Header";
import {Button} from "react-bootstrap";
import React from "react";

import './style.css'
import {Link} from "react-router-dom";

export default function ExpressReport({children}) {

    function collapseReportForm() {

        let toggleBox = document.getElementById('clicker')
        let reportForm = document.getElementById('fill-report-main')
        let labels = document.querySelectorAll('li label')
        let inputs = document.querySelectorAll('li > input, textarea, .form-select')
        let formContainer = document.getElementById('report-form-container')

        if (toggleBox.checked) {
            formContainer.style.padding = '15px 0 5px 75px'
            reportForm.style.marginRight = '30em';
            reportForm.style.paddingLeft = '45px';

            for (let i = 0; i < labels.length; i++) {
                labels[i].style.minWidth = '550px';
                labels[i].style.paddingLeft = '5px';
            }

            for (let i = 0; i < inputs.length; i++) {
                inputs[i].style.width = '500px';
                inputs[i].style.maxWidth = '500px';
            }
        } else {
            formContainer.style.padding = '15px 0 5px 15px'
            reportForm.style.marginRight = '0';
            reportForm.style.paddingLeft = '0';

            for (let i = 0; i < labels.length; i++) {
                labels[i].style.minWidth = '0';
                labels[i].style.paddingLeft = '60px';
            }

            for (let i = 0; i < inputs.length; i++) {
                inputs[i].style.width = '55%';
                inputs[i].style.maxWidth = '55%';
            }
        }
    }

    return(
        <div className="full-page">
            <Header/>
            <div className="fill-report">
                <section className="fill-report-sidebar">
                    <input id="clicker" type="checkbox" onClick={collapseReportForm} />
                    <label className="toggle-roll" htmlFor="clicker">Транскрипт<br/><span>&nbsp;разговора</span></label>
                    <div id="panel-wrap">
                        <div id="panel">
                            <p id="core-transcript-viewer" />
                            <p id="complete-transcript-viewer" />
                        </div>
                    </div>
                    <Link to="/dashboard">
                        <Button id="btn-dashboard-access">К контролю сеансом</Button>
                    </Link>
                </section>
                <section id="fill-report-main">
                    {children}
                </section>
            </div>
            {/* <Footer/> */}
        </div>
    );
}