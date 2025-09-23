import { Injectable } from "@angular/core";
import { SwUpdate, VersionEvent } from "@angular/service-worker";
import { BehaviorSubject, interval, Subject, throttleTime } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Injectable()
export class PwaVersionCheckerService {
    readonly isNewVersionAvailable$ = new BehaviorSubject<boolean>(false);
    private readonly _isPwaInstalled$ = new BehaviorSubject<boolean>(false);

    private readonly CHECK_INTERVAL_MILLISECONDS: number = 60 * 60 * 1000;
    private readonly AZURE_PROXY_CHECK_INTERVAL: number = 30 * 1000;
    private unsub = new Subject<void>();

    constructor(private swUpdate: SwUpdate) {
        if (!this.swUpdate.isEnabled) {
            return;
        }

        this.checkPwaInstallation();

        this.checkForUpdateOnce();
        this.setupCheckForUpdates();
        // this.setupAzureProxyAuthCheck();
    }

    get isPwaInstalled(): boolean {
        return this._isPwaInstalled$.getValue();
    }

    get isPwaInstalled$() {
        return this._isPwaInstalled$.asObservable();
    }

    private setIsPwaInstalled(value: boolean): void {
        this._isPwaInstalled$.next(value);
    }

    private checkPwaInstallation(): void {
        const isInstalled =
            window.matchMedia("(display-mode: standalone)").matches ||
            (window.navigator as any).standalone ||
            document.referrer.includes("android-app://");

        console.log(`PwaVersionCheckerService: isInstalled=${isInstalled}`);

        this.setIsPwaInstalled(isInstalled);
    }

    private checkForUpdateOnce(): void {
        if (!this.isPwaInstalled) {
            return;
        }

        this.swUpdate.checkForUpdate().then((hasUpdate: boolean) => {
            if (hasUpdate) {
                this.isNewVersionAvailable$.next(true);
            }
        });
    }

    setupCheckForUpdates(): void {
        this.unsub.next();

        if (!this.isPwaInstalled) {
            return;
        }

        this.swUpdate.versionUpdates
            .pipe(takeUntil(this.unsub))
            .pipe(throttleTime(this.CHECK_INTERVAL_MILLISECONDS))
            .subscribe((evt: VersionEvent) => {
                if (!this.isPwaInstalled) {
                    return;
                }

                switch (evt.type) {
                    case "VERSION_DETECTED":
                        console.log(
                            `Downloading new app version: ${evt.version.hash}`,
                        );
                        break;
                    case "VERSION_READY":
                        console.log(
                            `Current app version: ${evt.currentVersion.hash}`,
                        );
                        console.log(
                            `New app version ready for use: ${evt.latestVersion.hash}`,
                        );
                        this.isNewVersionAvailable$.next(true);
                        break;
                    case "VERSION_INSTALLATION_FAILED":
                        console.log(
                            `Failed to install app version '${evt.version.hash}': ${evt.error}`,
                        );
                        break;
                }
            });
    }

    private setupAzureProxyAuthCheck(): void {
        interval(this.AZURE_PROXY_CHECK_INTERVAL)
            .pipe(takeUntil(this.unsub))
            .subscribe(() => {
                this.checkForAzureProxyRedirect();
            });
    }

    private checkForAzureProxyRedirect(): void {
        fetch("/ngsw.json?ngsw-cache-bust=" + Math.random(), {
            method: "GET",
            redirect: "manual",
        })
            .then((response) => {
                if (this.isAzureProxyAuthRedirect(response)) {
                    console.log(
                        "Azure Proxy authentication redirect detected, forcing page reload",
                    );
                    document.location.reload();
                }
            })
            .catch((error) => {
                if (error.message && error.message.includes("CORS")) {
                    console.log(
                        "CORS error detected - likely Azure Proxy redirect, forcing page reload",
                    );
                    document.location.reload();
                } else if (
                    error.name === "TypeError" &&
                    error.message.includes("Failed to fetch")
                ) {
                    console.log(
                        "Network error during Azure Proxy check - likely authentication redirect, forcing page reload",
                    );
                    document.location.reload();
                } else {
                    console.log("Azure Proxy check failed:", error);
                }
            });
    }

    private isAzureProxyAuthRedirect(response: Response): boolean {
        if (response.type === "opaqueredirect" || response.status === 302) {
            return true;
        }

        const location = response.headers.get("location");
        if (location && location.includes("login.microsoftonline.com")) {
            return true;
        }

        const appProxyHeaders = [
            "x-ms-proxy-app-id",
            "x-ms-proxy-group-id",
            "x-ms-proxy-subscription-id",
        ];

        return appProxyHeaders.some((header) => response.headers.has(header));
    }

    applyUpdate(): void {
        document.location.reload();
    }
}
