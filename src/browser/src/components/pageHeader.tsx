import {useNavigate} from "react-router-dom";
import {useAuth} from "react-oidc-context";

export function Header() {
    const nav = useNavigate();
    const auth = useAuth();

    const signIn = () => {
        localStorage.setItem("redirectPath", location.pathname)
        auth.signinRedirect()
    }

    const renderAuthButtons = () => {
        if (auth.isAuthenticated) {
            return <>
                <div>Signed in as {auth.user?.profile.name}</div>
            <div onClick={() => auth.removeUser()}>Log out</div>
                </>
        } else {
            return <div onClick={signIn}>Log in</div>
        }
    }

    return (
        <div>
            <div className="hcContentContainer bgColorBrand1 hcMarginBottom5">
                <header className="hcPageHeaderSimple hcBasicSideMargin">
                    <div className="hcBrand">
                        <div className="hcBrandLogo">
                        </div>
                    </div>
                    <div className="hcSiteTitle" onClick={() => {nav('/')}}>
                        Occassio
                    </div>
                    {/*<div className="navi">*/}
                    {/*    <div onClick={() => {nav('/search')}}>Zoeken</div>*/}
                    {/*</div>*/}
                    <div className={"navi"}>
                    {
                        renderAuthButtons()
                    }
                    </div>
                </header>
            </div>
        </div>)
}
