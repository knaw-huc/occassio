import {useNavigate} from "react-router";
import {useEffect} from "react";

function AuthCallback () {
    const navigate = useNavigate()
    const redirectPath = localStorage.getItem("redirectPath") || "/"

    useEffect(() => {
        localStorage.removeItem("redirectPath")
        navigate(redirectPath)
    }, [])

    return <>
        <div>Signing in...</div>
    </>
}

export {AuthCallback}
