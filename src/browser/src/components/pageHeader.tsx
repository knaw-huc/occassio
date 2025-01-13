import {useNavigate} from "react-router-dom";

export function Header() {
    const nav = useNavigate();
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
                </header>
            </div>
        </div>)
}
