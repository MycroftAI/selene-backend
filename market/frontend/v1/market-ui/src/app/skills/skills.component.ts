import { Component, OnInit } from '@angular/core';

import { SkillsService } from './skills.service'

@Component({
  selector: 'marketplace-skills',
  templateUrl: './skills.component.html',
  styleUrls: ['./skills.component.scss']
})
export class SkillsComponent implements OnInit {
    public skillCategories: string[];
    public skills: Object;

    constructor(private skillsService: SkillsService) { }

    ngOnInit() {
        this.getAllSkills();
    }

    getAllSkills(): void {
        this.skillsService.getAllSkills().subscribe(
            (skills) => {
                this.skills = skills;
                this.get_skill_categories(skills);
            }
        )
    }

    get_skill_categories(skills): void {
        let skillCategories = [],
            systemCategoryFound = false;
        this.skillCategories = [];
        Object.keys(skills).forEach(
            categoryName => {skillCategories.push(categoryName);}
        );
        skillCategories.sort();

        // Make the "System" category display last, if it exists
        skillCategories.forEach(
            categoryName => {
                if (categoryName === 'System') {
                    systemCategoryFound = true;
                } else {
                    this.skillCategories.push(categoryName)
                }
            }
        );
        if (systemCategoryFound) {
            this.skillCategories.push('System')
        }
    }

    showSearchResults(searchResults): void {
        this.skills = searchResults;
        this.get_skill_categories(searchResults)
    }
}
