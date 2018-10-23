import { Component, OnInit } from '@angular/core';

import { SkillsService, AvailableSkill } from "../skills.service";
import { InstallService } from "../install.service";

@Component({
    selector: 'market-skill-summary',
    templateUrl: './skill-summary.component.html',
    styleUrls: ['./skill-summary.component.scss'],
})
export class SkillSummaryComponent implements OnInit {
    public skillCategories: string[];
    public availableSkills: AvailableSkill[];


    constructor(
        private installService: InstallService,
        private skillsService: SkillsService,
    ) { }

    ngOnInit() {
        this.getAvailableSkills();
    }

    getAvailableSkills(): void {
        this.skillsService.getAvailableSkills().subscribe(
            (skills) => {
                this.availableSkills = skills;
                this.skillCategories = this.skillsService.getSkillCategories();
                this.installService.getSkillInstallations();
            }
        )
    }

    filterSkillsByCategory(category: string): AvailableSkill[] {
        return this.availableSkills.filter(
            (skill) => skill.marketCategory === category
        );
    }

    showSearchResults(searchResults): void {
        this.availableSkills = searchResults;
        this.skillCategories = this.skillsService.getSkillCategories();
    }

}
