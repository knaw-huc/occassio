// import React from 'react';
import {useNavigate} from "react-router-dom";
// import logo from '../assets/img/logo-homepage-intro.svg';
// import "../assets/css/sport_style.css";

export function Header() {
    const nav = useNavigate();
    return (
        <div>
            <div className="hcContentContainer bgColorBrand1 hcMarginBottom5">
                <header className="hcPageHeaderSimple hcBasicSideMargin">
                    <div className="hcBrand">
                        <div className="hcBrandLogo">
                            {/*<img src={logo} className="logo"/>*/}
                        </div>
                    </div>
                    <div className="hcSiteTitle" onClick={() => {nav('/')}}>
                        Occassio
                    </div>
                    <div className="navi">
                        {/*<div onClick={() => {nav('/inleiding')}}>Inleiding</div>*/}
                        {/*<div onClick={() => {nav('/gymnastiek')}}>Sporten</div>*/}
                        <div onClick={() => {nav('/search')}}>Zoeken</div>
                        {/*<div onClick={() => {nav('/database')}}>Databank</div>*/}
                        {/*<div onClick={() => {nav('/literatuur')}}>Literatuur</div>*/}
                        {/*<div onClick={() => {nav('/colofon')}}>Colofon</div>*/}
                        {/*<div><Link to='mailto:resources@huygens.knaw.nl'>Contact</Link></div>*/}
                    </div>
                </header>
            </div>
        </div>)
}
