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

    applyInstallStatusChanges() {
        if (this.prevInstallStatuses) {
            Object.keys(this.newInstallStatuses).forEach(
                () => this.compareStatuses
            );
        }
        this.prevInstallStatuses = this.newInstallStatuses;
        this.installStatuses.next(this.newInstallStatuses);
    }

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

    installSkill(skill: AvailableSkill): Observable<Object> {
        return this.http.put<Object>(
            installUrl,
            {skill_name: skill.name}
        )
    }

    uninstallSkill(skill: AvailableSkill): Observable<Object> {
        return this.http.put<Object>(
            uninstallUrl,
            {skill_name: skill.name}
        )
    }
}
