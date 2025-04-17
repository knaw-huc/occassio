import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import {
    createBrowserRouter,
    Outlet,
    RouteObject,
    RouterProvider,
    ScrollRestoration,
    useRouteError
} from 'react-router-dom';
import './assets/css/occassio_style.scss';
import {
    App,
    createDetailLoader,
    createSearchLoader,
    Detail as BrowserDetail,
    Search,
    SearchParams,
    searchUtils
} from '@knaw-huc/browser-base-react';
import ListItem from "./components/listItem";
import Facets from "./components/facets";
import {Detail} from "./components/detail";
import {getApiBase} from "./misc/config.ts";
import {Header} from "./components/pageHeader.tsx";
import {AuthCallback} from "./auth/AuthCallback.tsx";
import {ProtectedRoute} from "./auth/ProtectedRoute.tsx";
import {AuthProvider, useAuth} from "react-oidc-context";
import {OidcConfig} from "./OIDC-config.ts";

const header = <Header />
const searchLoader = createSearchLoader(
    searchUtils.getSearchObjectFromParams,
    getApiBase() + '/api/browse',
    10,
    'desc',
);
const detailLoader = createDetailLoader(id => getApiBase() + `/api/article?rec=${id}`);
const title = "Occassio";

function Router() {
    const auth = useAuth();
    const token = auth.user?.access_token

    const routes: RouteObject[] = [
        {
            element: <App header={header}>
                <ScrollRestoration />
                <Outlet />
            </App>,
            children: [
                {
                    path: '/oidc/redirect',
                    element: <AuthCallback />,
                },
                {
                    element: <ProtectedRoute />,
                    children: [
                        {
                            path: '/',
                            loader: async ({request}) => {
                                const headers: {Authorization?: string} = {}
                                if (token) {
                                    headers['Authorization'] = `Bearer ${token}`
                                }
                                return searchLoader(new URL(request.url).searchParams, headers)
                            },
                            element: <Search
                                pageLength={30}
                                ResultItemComponent={ListItem}
                                facetsElement={<Facets />}
                                withPaging={true}
                                hasIndexPage={false}
                                showSearchHeader={false}
                                updateDocumentTitle={false}
                                searchParams={SearchParams.PARAMS} />,
                            errorElement: <ErrorBoundary />,
                        },
                        {
                            path: '/detail/:id',
                            loader: async ({params}) => {
                                const headers: {Authorization?: string} = {}
                                if (token) {
                                    headers['Authorization'] = `Bearer ${token}`
                                }
                                return detailLoader(params.id as string, headers)
                            },
                            element: <BrowserDetail title={title} updateDocumentTitle={false} DetailComponent={Detail} />,
                            errorElement: <ErrorBoundary />,
                        }
                    ],
                    errorElement: <ErrorBoundary />,
                }
            ]
        }
    ]

    return <>
        <RouterProvider router={createBrowserRouter(routes)} />
    </>
}

function ErrorBoundary() {
    const error = useRouteError()
    console.error(error)
    return <h1>Error loading page</h1>
}

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
    <React.StrictMode>
        <AuthProvider {...OidcConfig}>
            <Router />
        </AuthProvider>
    </React.StrictMode>
);
