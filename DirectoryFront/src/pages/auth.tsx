import {useState} from 'react'
import {sign_up, login} from "../api/auth"
import './auth.css'

function AuthPage() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [isLogin, setIsLogin] = useState(false)

    const handleSignUp = async () => {
        try {
            const response = await sign_up(username, password);
            console.log(response.data)
        } catch (error) {console.error(error)}
    }
    const handleLogin = async () => {
        try {
            const response = await login(username, password);
            console.log(response.data)
        } catch (error) {console.error(error)}
    }

    return (
        <div className="container">
            <p className="authText">{isLogin ? "login" : "sign_up"}</p>
            <form>
                <label>Username</label>
                <input type="text"
                       className="username_input"
                       value={username}
                       onChange={(e) => setUsername(e.target.value)} />
                <label>Password</label>

                <input type="password"
                       className="password_input"
                       value={password}
                       onChange={(e) => setPassword(e.target.value)} />
            </form>
                <button className="sendButton" onClick={isLogin ? handleLogin : handleSignUp}>Send</button>
                <p className="choice"
                   onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "sign_up" : "login"}</p>
        </div>
    )
}

export default AuthPage