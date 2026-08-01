import { BrowserRouter, Routes, Route } from "react-router-dom";
import AuthPage from '../pages/auth.tsx'

function AppRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<AuthPage />} />
            </Routes>
        </BrowserRouter>
    )
}

export default AppRouter;