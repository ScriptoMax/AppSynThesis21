import React from 'react';
import {Link, useHistory} from 'react-router-dom';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import * as HardAwesome from '@fortawesome/free-solid-svg-icons'
import SessionControlAction from "../../ControlAction";
import './style.css';
import api from "../../../services/api";

import './../../../config'

export default function Header(props) {

    let sessionControl = new SessionControlAction()
    const name = localStorage.getItem('userName');
    const history = useHistory();

    async function handleLogout(e) {

        e.preventDefault();
        let sessionStatus = localStorage.getItem('sessionStatus')

        if (sessionStatus === 'active')
            await sessionControl.handleCancelRequest().then(r => console.log('session is close'))

        try {
            await api.post('session/logout/', {
                user_id: localStorage.getItem('userId')
            },{
                headers: {
                    'Authorization': localStorage.getItem('userToken')
                }
            }).then( response => {
                let resultCode = response.status
                console.log('server response code: ' + resultCode)
            }).catch( err => {
                console.log(err)
            });
            let counter = 0
            for (let i of global.config.i18n.sockets) {
                i = null
                counter++
                console.log('socket #' + counter)
            }

            history.push('/')
        } catch(err) {
            alert('Session opening refused as request includes incomplete or wrong parameters')
        }
        localStorage.clear();
    }

    return (
        <div className="container-header">
            <div className="logo">
                <Link to="/dashboard" style={{ textDecoration: 'none' }}>
                <h1 style={{ 'color': 'black' }}>DemoDesk UI</h1>
                </Link>
            </div>
            <div className="header-menu">
                <ul>
                    <li>
                        <FontAwesomeIcon
                            icon={HardAwesome.faUserCircle} size="2x" style={{ verticalAlign: 'middle', marginRight: '5px' }} />
                         { name }
                    </li>
                    <li style={{ marginRight : '15px' }}>
                        <Link onClick={handleLogout} to="/">
                        <FontAwesomeIcon icon={HardAwesome.faSignOutAlt} size="2x" style={{ color: 'black' }} />
                        </Link>
                    </li>
                </ul>
            </div>
        </div>
    );
}