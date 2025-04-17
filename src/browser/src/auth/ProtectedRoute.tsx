import {useAuth} from "react-oidc-context";
import {Outlet, useLocation} from "react-router-dom";

function ProtectedRoute() {
    const auth = useAuth();
    const location = useLocation();

    const signIn = () => {
        localStorage.setItem("redirectPath", location.pathname)
        auth.signinRedirect()
    }

    if (auth.isLoading) {
        return <>
            <div className={"row"}>
                <div className={"main-content"}>
                    <div className={"justify hcMarginBottom1"}>
                        <h2 className={"hcMarginBottom2"}>Loading...</h2>
                    </div>
                </div>
            </div>
        </>
    }
    if (!auth.isAuthenticated) {
        return <>
            <div className={"row"}>
                <div className={"main-content"}>
                    <div className={"justify hcMarginBottom1"}>
                        <h2 className={"hcMarginBottom2"}>You need to be logged in to view this page.</h2>
                        <button onClick={signIn}>Log in with SRAM</button>
                    </div>
                </div>
            </div>
        </>
    }
    if (auth.isAuthenticated) {
        return <>
            <Outlet/>
        </>
    }
}

export {ProtectedRoute}
