import { User, UserManager } from "oidc-client-ts";
import {OidcConfig} from "../OIDC-config.ts";

export default class AuthService {
    userManager: UserManager;

    constructor() {
        this.userManager = new UserManager(OidcConfig);
    }

    public getUser(): Promise<User | null> {
        return this.userManager.getUser();
    }

    public login(): Promise<User | null> {
        return this.userManager.signinRedirect()
            .then(this.getUser)
            .catch(error => {
                console.error(error)
                return null
            });
    }

    public loginCallback(): Promise<User> {
        // @ts-ignore
        return this.userManager.signinCallback();
    }

    public logout(): Promise<void> {
        return this.userManager.signoutRedirect();
    }
}
