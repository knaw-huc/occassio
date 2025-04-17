import {WebStorageStateStore} from "oidc-client-ts";
import {getOidcClientId, getOidcIssuer, getOidcRedirectUri} from "./misc/config.ts";

export const OidcConfig = {
    authority: getOidcIssuer(),
    client_id: getOidcClientId(),
    redirect_uri: getOidcRedirectUri(),
    scope: "openid profile email openid aarc orcid uid",
    loadUserInfo: true,
    userStore: new WebStorageStateStore({store: window.localStorage})
}
