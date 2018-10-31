import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { AvailableSkill, SkillDetail } from './skills.service';

// Status values that can be expected in the install status endpoint response.
type InstallStatus = 'failed' | 'installed' | 'installing' | 'uninstalling';

export interface SkillInstallStatus {
    [key: string]: InstallStatus;
}

export interface FailureReason {
    [key: string]: string;
}

export interface Installations {
    failureReasons: FailureReason;
    installStatuses: SkillInstallStatus;
}

const inProgressStatuses = ['installing', 'uninstalling', 'failed'];
const installStatusUrl = '/api/skill/installations';
const installerSettingsUrl = '/api/skill/install';

@Injectable({
    providedIn: 'root'
})
export class InstallService {
    public failureReasons: FailureReason;
    public installStatuses = new Subject<SkillInstallStatus>();
    public newInstallStatuses: SkillInstallStatus;
    private prevInstallStatuses: SkillInstallStatus;
    public statusNotifications = new Subject<string[]>();

    constructor(private http: HttpClient) { }

    /** Issue API call to get the current state of skill installations */
    getSkillInstallations() {
        this.http.get<Installations>(installStatusUrl).subscribe(
            (installations) => {
                this.newInstallStatuses = installations.installStatuses;
                this.failureReasons = installations.failureReasons;
                this.applyInstallStatusChanges();
                this.checkInstallationsInProgress();
            }
        );
    }

    /** Emit changes to install statuses */
    applyInstallStatusChanges() {
        if (this.prevInstallStatuses) {
            Object.keys(this.prevInstallStatuses).forEach(
                (skillName) => { this.compareStatuses(skillName); }
            );
        }
        this.prevInstallStatuses = this.newInstallStatuses;
        this.installStatuses.next(this.newInstallStatuses);
    }

    /** Compare the new status to the previous status looking for changes
     *
     * There is a race condition where the skill status on the device may not
     * change between the time a user clicks a button in the marketplace and
     * the next call of the status endpoint.
     *
     * For example, there is a period of time between the install button
     * on the marketplace being clicked and device(s) retrieving that request.
     * If the skill status endpoint is called within this time frame the status
     * on the response object will not be 'installing'.  This would result in
     * the status reverting to its previous state.
     *
     * To combat this, we check that skill status changes follow a predefined
     * progression before reflecting the status change on the UI.
     */
    compareStatuses(skillName: string) {
        const prevSkillStatus = this.prevInstallStatuses[skillName];
        const  newSkillStatus = this.newInstallStatuses[skillName];

        switch (prevSkillStatus) {
            case ('installing'): {
                if (newSkillStatus === 'installed') {
                    this.statusNotifications.next([skillName, newSkillStatus]);
                    this.removeFromInstallQueue(skillName).subscribe();
                } else if (newSkillStatus === 'failed') {
                    this.statusNotifications.next([skillName, 'install failed']);
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
            case ('uninstalling'): {
                if (!newSkillStatus) {
                    this.statusNotifications.next([skillName, 'uninstalled']);
                    this.removeFromUninstallQueue(skillName).subscribe();
                } else if (newSkillStatus === 'failed') {
                    this.statusNotifications.next([skillName, 'uninstall failed']);
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
            case ('failed'): {
                if (!newSkillStatus) {
                    this.statusNotifications.next([skillName, 'uninstalled']);
                } else if (newSkillStatus !== 'installed') {
                    this.statusNotifications.next([skillName, newSkillStatus]);
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
        }
    }

    /***
     * Return the install status for the specified skill.
     *
     * System skills are treated differently than installed skills because they
     * cannot be removed from the device.  This function will make the differentiation.
     *
     * @param skillName: unique name of skill being installed
     * @param isSystemSkill: skill that has a "system" tag
     * @param installStatuses: object containing all device skills and their status
     */
    getSkillInstallStatus(
            skillName: string,
            isSystemSkill: boolean,
            installStatuses: SkillInstallStatus
    ) {
        let installStatus: string;

        if (isSystemSkill) {
            installStatus = 'system';
        } else {
            installStatus = installStatuses[name];
        }

        return installStatus;
    }

    /** Poll at an interval to check the status of install/uninstall requests
     *
     * We want to avoid polling if we don't need it.  Only poll if waiting for
     * the result of a requested install/uninstall.
     */
    checkInstallationsInProgress() {
        const inProgress = Object.values(this.newInstallStatuses).filter(
            (installStatus) => inProgressStatuses.includes(installStatus)
        );
        if (inProgress.length > 0) {
            setTimeout(() => { this.getSkillInstallations(); }, 10000);
        }
    }

    /**
     * Call the API to add a skill to the Installer skill's 'to_install' setting.
     *
     * @param skillName: the skill being installed
     */
    addToInstallQueue(skillName: string): Observable<Object> {
        return this.http.put<Object>(
            installerSettingsUrl,
            {
                action: 'add',
                section: 'to_install',
                skill_name: skillName
            }
        );
    }

    /**
     * Call the API to add a skill to the Installer skill's 'to_remove' setting.
     *
     * @param skillName: the skill being removed
     */
    addToUninstallQueue(skillName: string): Observable<Object> {
        return this.http.put<Object>(
            installerSettingsUrl,
            {
                action: 'add',
                section: 'to_remove',
                skill_name: skillName
            }
        );
    }

    /**
     * Call the API to remove a skill to the Installer skill's 'to_install' setting.
     *
     * @param skillName: the skill being installed
     */
    removeFromInstallQueue(skillName: string): Observable<Object> {
        return this.http.put<Object>(
            installerSettingsUrl,
            {
                action: 'remove',
                section: 'to_install',
                skill_name: skillName
            }
        );
    }

    /**
     * Call the API to remove a skill to the Installer skill's 'to_remove' setting.
     *
     * @param skillName: the skill being removed
     */
    removeFromUninstallQueue(skillName: string): Observable<Object> {
        return this.http.put<Object>(
            installerSettingsUrl,
            {
                action: 'remove',
                section: 'to_remove',
                skill_name: skillName
            }
        );
    }
}
