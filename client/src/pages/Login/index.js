import React, { useState } from 'react';

import './style.css';
import Logscreen from '../../assets/images/logscreen.png';
import { useHistory } from 'react-router-dom';
import api from '../../services/api'

export default function Login() {

    const [ user_name, setUserName ] = useState('');
    const [ password, setPassword ] = useState('');

    const history = useHistory();

    async function handleSubmit(e) {
        
        e.preventDefault();
        
        try {
            localStorage.setItem('userName', user_name)
            const response = await api.post('session/login/', {user_name, password});
            let userId = response.data['user_id']
            let token = response.data['user_token']
            //console.log('Django response: 1) id = ' + userId + ' 2) token = ' + token);
            localStorage.setItem('userToken', token);
            localStorage.setItem('userId', userId)
            localStorage.setItem('sessionStatus', 'close')
            localStorage.setItem('baseCategory', '')
            localStorage.setItem('subcategory', '')
            localStorage.setItem('lastActiveSpeaker', '')
            history.push('/dashboard');
        } catch(err) {
            alert('User name or password is wrong\nFix incorrect inputs to retry login')
        }
    }

    return(
        <div className="base-login">
        <div className="container component-login">
            <div className="container logo">
                <img src={Logscreen} alt="Auth form"/>
            </div>
            <div className="container container-login">
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        className="input"
                        placeholder="User name"
                        value={user_name}
                        onChange = { e => {setUserName(e.target.value)}}
                    />
                    <input 
                        type="password"
                        className="input"
                        placeholder="Password"
                        value={password}
                        onChange = { e => {setPassword(e.target.value) }}
                    />

                    <div className="container component-link">
                        <button id="login-submit-btn" type="submit" className="button">Log in</button>
                    </div>
                </form>
            </div>
        </div>
        </div>
    );
}