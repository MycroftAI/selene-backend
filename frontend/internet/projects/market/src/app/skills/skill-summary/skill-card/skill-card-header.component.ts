/**
 * Format the header portion of a skill summary card.  This includes the icon
 * for the skill and a Mycroft logo if the skill is authored by Mycroft AI.
 */
import { Component, Input, OnInit } from '@angular/core';
import { AvailableSkill } from '../../skills.service';
import { InstallService } from '../../install.service';
import { faCheckCircle } from '@fortawesome/free-solid-svg-icons';

@Component({
    selector: 'market-skill-card-header',
    templateUrl: './skill-card-header.component.html',
    styleUrls: ['./skill-card-header.component.scss']
})
export class SkillCardHeaderComponent implements OnInit {
    public isInstalled: boolean;
    public installedIcon = faCheckCircle;
    @Input() public skill: AvailableSkill;

    constructor(private installService: InstallService) { }

    /**
     * Include the Mycroft AI logo in the card header if Mycroft authored the skill
     */
    ngOnInit() {
        this.installService.installStatuses.subscribe(
            (installStatuses) => {
                const installStatus = this.installService.getSkillInstallStatus(
                    this.skill.name,
                    this.skill.isSystemSkill,
                    installStatuses
                );
                this.isInstalled = ['system', 'installed'].includes(installStatus);
            }
        );
    }
}
