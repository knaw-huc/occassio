export const FACET_URL = '/api/facet';

const oidcIssuer = "$VITE_OIDC_ISSUER";
const oidcClientId = "$VITE_OIDC_CLIENT_ID";
const oidcRedirectUri = "$VITE_OIDC_REDIRECT_URI";
const apiBase = "$VITE_API_BASE";

export const getOidcIssuer = () => getVar(oidcIssuer);

export const getOidcClientId = () => getVar(oidcClientId);

export const getOidcRedirectUri = () => getVar(oidcRedirectUri);

export const getApiBase = () => getVar(apiBase);

function getVar(key: string) {
    if (key.startsWith('$VITE_'))
    {
        return key.substring(1) in import.meta.env ? import.meta.env[key.substring(1)] : '';
    }
    return key;
}
