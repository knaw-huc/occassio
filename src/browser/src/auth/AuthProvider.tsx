import {createContext, useContext, useState} from "react";
import AuthService from "./AuthService.ts";
import {User} from "oidc-client-ts";

interface AuthContextType {
    user: any
    login: Function
    logout: Function
    loginCallback: Function
}

const AuthContext = createContext<AuthContextType>(null!)

const useAuth = () => useContext(AuthContext)

function AuthProvider({children}: {children: React.ReactNode}) {
    const [user, setUser] = useState<User | null | undefined>(
        JSON.parse(
            sessionStorage.getItem('user-data'!) || "null"
        ) || undefined
    )
    const authService = new AuthService()

    const login = () => authService.login().then(u => setUser(u))

    const loginCallback = async () => {
        const authedUser = await authService.loginCallback()
        setUser(authedUser)
    }

    const logout = () => authService.login().then(() => setUser(null))
    const value = {user, login, logout, loginCallback}

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export {AuthProvider, useAuth}
