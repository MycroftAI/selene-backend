import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, Subject } from "rxjs";
import { AvailableSkill, SkillDetail } from "./skills.service";

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

// const inProgressStatuses = ['installing', 'uninstalling', 'failed'];
const inProgressStatuses = ['installing', 'uninstalling'];
const installStatusUrl = '/api/skill/installations';
const installUrl = '/api/skill/install';
const uninstallUrl = '/api/skill/uninstall';

@Injectable({
    providedIn: 'root'
})
export class InstallService {
    public failureReasons: FailureReason;
    public installStatuses = new Subject<SkillInstallStatus>();
    public newInstallStatuses: SkillInstallStatus;
    private prevInstallStatuses: SkillInstallStatus;
    public statusNotifications = new Subject<SkillInstallStatus>();

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
        )
    }

    /** Emit changes to install statuses */
    applyInstallStatusChanges() {
        if (this.prevInstallStatuses) {
            Object.keys(this.newInstallStatuses).forEach(
                () => this.compareStatuses
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
     * on the response object will not be "installing".  This would result in
     * the status reverting to its previous state.
     *
     * To combat this, we check that skill status changes follow a predefined
     * progression before reflecting the status change on the UI.
     */
    compareStatuses(skillName: string) {
        let prevSkillStatus = this.prevInstallStatuses[skillName];
        let newSkillStatus = this.newInstallStatuses[skillName];
        let statusNotifications: SkillInstallStatus = {};

        switch (prevSkillStatus) {
            case ('installing'): {
                if (['installed', 'failed'].includes(newSkillStatus)) {
                    statusNotifications[skillName] = newSkillStatus;
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
            case ('uninstalling'): {
                if (!newSkillStatus || newSkillStatus === 'failed') {
                    statusNotifications[skillName] = newSkillStatus;
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
            case ('failed'): {
                if (!newSkillStatus || newSkillStatus != 'installed') {
                    statusNotifications[skillName] = newSkillStatus;
                } else {
                    this.newInstallStatuses[skillName] = prevSkillStatus;
                }
                break;
            }
        }

        if (statusNotifications) {
            this.statusNotifications.next(statusNotifications)
        }

    }

    /***
     * Return the install status for the specified skill.
     *
     * System skills are treated differently than installed skills because they
     * cannot be removed from the device.  This function will make the differentiation.
     *
     * @param skill: single skill object, available or detail
     * @param installStatuses: object containing all device skills and their status
     */
    getSkillInstallStatus(
            skill: AvailableSkill | SkillDetail,
            installStatuses: SkillInstallStatus
    ) {
        let installStatus: string;

        if (skill.isSystemSkill) {
            installStatus = 'system';
        } else {
            installStatus = installStatuses[skill.name];
        }

        return installStatus;
    }

    /** Poll at an interval to check the status of install/uninstall requests
     *
     * We want to avoid polling if we don't need it.  Only poll if waiting for
     * the result of a requested install/uninstall.
     */
    checkInstallationsInProgress() {
        let inProgress = Object.values(this.installStatuses).filter(
            (installStatus) => inProgressStatuses.includes(installStatus)
        );
        if (inProgress.length > 0) {
            setTimeout(() => {this.getSkillInstallations();}, 10000);
        }
    }

    /**
     * Call the API endpoint for installing a skill.
     *
     * @param skill: the skill being installed
     */
    installSkill(skill: AvailableSkill): Observable<Object> {
        return this.http.put<Object>(
            installUrl,
            {skill_name: skill.name}
        )
    }

    /**
     * Call the API endpoint for uninstalling a skill.
     *
     * @param skill: the skill being removed
     */
    uninstallSkill(skill: AvailableSkill): Observable<Object> {
        return this.http.put<Object>(
            uninstallUrl,
            {skill_name: skill.name}
        )
    }
}
